package speed

import (
	"fmt"
	"math"
	"math/rand"
	"time"

	"github.com/go-logr/logr"
)

const (
	// TickDistance is the linear distance traveled by the encoder in one tick (in meters)
	TickDistance float64 = 0.00179267
	// ForwardDirection is used to select if CW is forward or backwards (1 or -1)
	ForwardDirection int32 = 1
	// SpeedCommandPause is the command to pause the gathering of data
	SpeedCommandPause Command = "pause"
	// SpeedCommandRestartRestart is the command to restart the gathering of data
	SpeedCommandRestart Command = "restart"
	// SpeedCommandReset is the command to put the position to zero
	SpeedCommandReset Command = "reset"
	// SpeedCommandCalibrate is the command to adjust the delta increments of movement
	SpeedCommandCalibrate Command = "calibrate"
	// SpeedCommandSimulate gnerate random data simulating an exercise
	SpeedCommandSimulate Command = "simulate"
	// PullUpThresholdStart is the increment in position to consider a pull up started (in meters)
	PullUpThresholdStart = 0.2
	// PullUpThresholdEnd is the decrement of position, relative to the maximum, which decides we have finished the pull up (in meters)
	PullUpThresholdEnd = 0.2
	// PausedMessage message send to the client when the app is not ready to run
	PausedMessage = "Pause"
	// StartMessage message send to the client when the app is ready to measure pull ups
	StartMessage = "Ready"
	// EndExerciseTimeThreshold is the duration to consider the climber has finished if no new evets are received
	EndExerciseTimeThreshold time.Duration = 1 * time.Second
	// EndExerciseDistanceThreshold is the distance to consider the climber is still, in meters
	EndExerciseDistanceThreshold float64 = 0.05
)

// Speed represents the structure to measure speed
//
// Diagram of methods and channels
// eyJjb2RlIjoiZ3JhcGggVERcbiAgJSVBW1J1blNwZWVkXVxuICBCW0NhcHR1cmVdXG4gIENbQ29hY2hdXG4gIERbUHJvY2Vzc11cbiAgRXtDbGllbnR9XG4gIEZbKFN0b3JlKV1cbiAgJSVBIC0tc3RhcnQtLT4gQlxuICAlJUEgLS1zdGFydC0tPiBDXG4gICUlQSAtLXN0YXJ0LS0
// graph TD
//  %%A[RunSpeed]
//  B[Capture]
//  C[Coach]
//  D[Process]
//  E{Client}
//  F[(Store)]
//  %%A --start--> B
//  %%A --start--> C
//  %%A --start--> D
//  B --rawData--> D
//  E --control--> C
//  D --data--> C
//  C --procCtrl--> D
//  D --store--> F
//  C --store--> F
//  C --client--> E
//
type Speed struct {
	Log    logr.Logger
	Device string
	// ClientSampling defines how often should be sent data to the client
	ClientSampling time.Duration
	// ExportChannel used to share calculated data
	ExportChannel chan<- ExportData
	// BackendCmdChannel is used to signal client from start and end detection
	BackendCmdChannel chan<- BackendCmd
	// ControlChannel pass commands from the client to the coach
	ControlChannel chan Control
	// ClientMessagesChannel used by the coach to send messages to the client
	ClientMessagesChannel chan<- ClientMsg

	// rawDataChannel pass data from the capturer to the processor
	rawDataChannel chan EncoderRawData
	// dataChannel pass data from the processor to the coach
	dataChannel chan Data
	// processorControlChannel used by the coach to control the processor
	processorControlChannel chan Control
	// calculatorPullUpActive marks if a pull up is being done
	calculatorPullUpActive bool
	// calculatorPullUpNumber stores the number of pull ups of the serie
	calculatorPullUpNumber int
	// calculatorPullUpMaxSpeed stores the max speed of the serie
	calculatorPullUpMaxSpeed float64
	// calculatorPullUpLastSpeed stores the speed of the last pull up
	calculatorPullUpLastSpeed float64
	// calculatorMinDistance stores the min distance seen after starting a set
	// Used to calculate the start of a pull up
	calculatorMinDistance float64
	// calculatorMaxDistance stores the highes point reached doing a pull up.
	// Used to decide when a pull has ended and if next pull ups are being done correctly
	calculatorMaxDistance float64
	// calculatorLatestValues stores latest data seen by the calculator and it is used to decide if climber has finished
	calculatorLatestValues []Data

	// exerciseActive defines if the climber is performing an exercise
	exerciseActive bool

	// alarmSpeedLoss define the threshold to warn the user of a considerable loss of speed
	alarmSpeedLoss float64

	// active defines if the coach is ready or not
	active bool
}

// ClientMsg responses to the client after a command is received
type ClientMsg struct {
	Value string
}

// SpeedCommand are the available commands to send to the Coach
type Command string

// Control is used to pass command from the ws client to the speed program
type Control struct {
	Type  Command
	Value float64
}

// EncoderRawData represents an event from the linear encoder.
// value have the direction (value -1 or 1).
// timeNs is the time, in nanoseconds
type EncoderRawData struct {
	value  int32
	timeNs int64
}

// BackendCmd used to send commands to the client
// TODO refactor names to clarify usage
type BackendCmd struct {
	Command *string
	Value   *float64
}

// SpeedData represents the useful data generated from each event
type Data struct {
	Position float64
	Speed    float64
	Time     time.Time
}

// ExportData is the data exported to be used by the external APIs
type ExportData struct {
	Id        int
	Position  float64
	Speed     float64
	Time      time.Time
	PullUps   *int
	SpeedLoss *float64
	LastSpeed *float64
	MaxSpeed  *float64
}

// RunSpeed starts the goroutines to measure and process speed
func (s *Speed) RunSpeed() {
	s.Log.V(3).Info("start speed")

	// TODO cuanto espacio poner en estos canales?
	s.rawDataChannel = make(chan EncoderRawData, 100)
	s.dataChannel = make(chan Data, 10)
	s.processorControlChannel = make(chan Control, 10)

	go s.Capture(s.rawDataChannel)
	go s.Process(s.rawDataChannel, s.processorControlChannel, s.dataChannel)
	go s.Coach(s.dataChannel, s.ControlChannel, s.processorControlChannel)

}

// Process get raw events and calculate position and speed.
// Send the data to the coach
// Could be controlled by the coach (to pause, reset, etc)
func (s *Speed) Process(rawDataCh <-chan EncoderRawData, procControlCh <-chan Control, dataCh chan<- Data) {
	s.Log.V(3).Info("start speed process")
	var position float64 = 0
	var lastTime int64 = 0
	// TODO quitar cuando lo tengamos calibrado? O dejar para poder usar en el futuro?
	calibrationFactor := 0.0

	// control if generated data should be sent to the encoderData channel
	sendEvents := true

	for {
		select {
		// TODO sacar de aqui los comandos que son del coach
		case c := <-procControlCh:
			switch c.Type {
			case SpeedCommandPause:
				sendEvents = false
			case SpeedCommandRestart:
				sendEvents = true
			case SpeedCommandReset:
				position = 0
			case SpeedCommandCalibrate:
				calibrationFactor += c.Value
				s.Log.V(2).Info("calibrate", "value", c.Value, "calibrationFactor", calibrationFactor)
			}

		case e := <-rawDataCh:
			s.Log.V(5).Info("process linear encoder", "event.value", e.value, "event.timeNs", e.timeNs)
			deltaPosition := float64(ForwardDirection*e.value) * (TickDistance + calibrationFactor)
			position += deltaPosition
			// Speed in meters/sec
			speed := deltaPosition / (float64(e.timeNs-lastTime) / 1e9)
			lastTime = e.timeNs

			if sendEvents {
				// Convert time in nanoseconds to go time (epoch sec, epoch ns)
				t := time.Unix(e.timeNs/1e9, e.timeNs-(e.timeNs/1e9)*1e9)

				// Send data without blocking. Let the processor run if the client or db queues are full
				select {
				case dataCh <- Data{position, speed, t}:
					s.Log.V(5).Info("sent processed linear encoder event to coach", "position", position, "speed", speed)
				default:
					s.Log.Error(fmt.Errorf("coach channel is full"), "not able to send data", "position", position, "speed", speed)
				}
			}
		}
	}
}

// Coach get the data processed and calculates useful info for the client
// dataCh should be receive only, but we send data on it with the simulation command
func (s *Speed) Coach(dataCh chan Data, controlCh <-chan Control, processorControlCh chan<- Control) {
	// Defines if coach is working
	s.active = false
	// Used to signal the calculator to reset to initial state
	reset := false

	// Store the last time a value was pushed to the client
	var previousSent time.Time
	// Uniq identifier for each of the metric sent
	var id int

	// The coach only receive events in the case of a external command or if the climber moves.
	// We need to detect a finished exercise if the climber stays still, so we need to generate events
	ticker := time.NewTicker(250 * time.Millisecond)

	for {
		select {
		case c := <-controlCh:
			s.Log.V(2).Info("coach command", "cmd", c.Type)
			switch c.Type {
			case SpeedCommandPause:
				s.active = false
				s.exerciseActive = false
				// Pause the gather of metrics
				processorControlCh <- c
				s.sendClientMsg(PausedMessage)
			case SpeedCommandRestart:
				s.active = true
				// Reset signal to calculator
				reset = true
				// Restart the gather of metrics
				processorControlCh <- c
				s.sendClientMsg(StartMessage)
			case SpeedCommandReset:
				// Just send the command to the processor
				processorControlCh <- c
				s.sendClientMsg("Reset done")
			case SpeedCommandCalibrate:
				// Just send the command to the processor
				processorControlCh <- c
				s.sendClientMsg("Calibration done")
			case SpeedCommandSimulate:
				s.sendClientMsg("Simulation start")

				// Pause the generator
				processorControlCh <- Control{SpeedCommandPause, 0}

				go func() {
					rand.Seed(time.Now().UnixNano())
					pullups := rand.Intn(6) + 1
					maxSpeed := rand.Float64() + 0.5
					distance := rand.Float64()*0.2 + 0.5
					loss := float64(rand.Intn(25)) / 100.0
					sampling := 10 * time.Millisecond

					s.Log.V(3).Info("Speed simulator",
						"pullups", pullups,
						"maxSpeed", maxSpeed,
						"distance", distance,
						"sleep", sampling.Seconds(),
						"loss", loss,
					)

					// Send some small values to simulate the first events before the pullup
					for i := 0; i < 3; i++ {
						dataCh <- Data{
							Position: 0.01,
							Speed:    0.01,
							Time:     time.Now(),
						}
						time.Sleep(100 * time.Millisecond)
					}

					for i := 0; i < pullups; i++ {
						maxSpeedPullup := maxSpeed - (maxSpeed * float64(i) * loss / float64(pullups-1))
						// Convert to ns and add some time, because not all pullup is a fastest speed
						duration := time.Duration(1e9*distance*2/maxSpeedPullup) + 300*time.Millisecond
						steps := (duration.Seconds() / sampling.Seconds())

						s.Log.V(4).Info("pullup",
							"pullup", i,
							"maxSpeedPullup", maxSpeedPullup,
							"duration", duration.Seconds(),
							"steps", steps,
							"max", math.Pi)

						for j := 0.0; j < math.Pi; j += math.Pi / steps {
							position := math.Sin(j)
							speed := math.Sin(j*2) * maxSpeedPullup
							dataCh <- Data{
								Position: position,
								Speed:    speed,
								Time:     time.Now(),
							}

							time.Sleep(sampling)
						}
					}

				}()
			default:
				s.Log.Error(fmt.Errorf("unkown command"), "coach", "type", c.Type)
			}

		case d := <-dataCh:
			if s.active {
				numberPullUps, speedLoss, lastSpeed, maxSpeed, controlCmd := s.Calculator(d, reset)
				reset = false

				s.Log.V(4).Info("send data to client",
					"position", d.Position,
					"speed", d.Speed,
					"pullUps", numberPullUps,
					"lossSpeed", speedLoss,
					"lastSpeed", lastSpeed,
					"maxSpeed", maxSpeed,
					"controlCmd", controlCmd,
				)

				// Send backend commands to the client
				// Sends start and end events
				if controlCmd != nil {
					select {
					case s.BackendCmdChannel <- *controlCmd:
					default:
						s.Log.Error(fmt.Errorf("channel full"), "Cannot send data", "channel", "BackendCmdChannel")
					}
				}

				// Do not send data to the client faster than ClientSampling
				now := time.Now()
				if now.Sub(previousSent) < s.ClientSampling {
					continue
				}
				previousSent = now
				id++

				select {
				case s.ExportChannel <- ExportData{
					Id:        id,
					Position:  d.Position,
					Speed:     d.Speed,
					Time:      time.Time{},
					PullUps:   numberPullUps,
					SpeedLoss: speedLoss,
					LastSpeed: lastSpeed,
					MaxSpeed:  maxSpeed,
				}:
				default:
					s.Log.Error(fmt.Errorf("channel full"), "Cannot send data", "channel", "ExportData")
				}
			}
		case <-ticker.C:
			if s.exerciseActive && time.Now().Sub(previousSent) > EndExerciseTimeThreshold {
				s.Log.V(3).Info("Exercise finished detection because no movement", "threshold", EndExerciseTimeThreshold, "previousSent", previousSent)

				// End event
				c := "end"
				v := float64(previousSent.UnixNano()) / 1e9
				startCommand := BackendCmd{&c, &v}
				cmd := &startCommand
				s.exerciseActive = false

				select {
				case s.BackendCmdChannel <- *cmd:
				default:
					s.Log.Error(fmt.Errorf("channel full"), "Cannot send data", "channel", "BackendCmdChannel")
				}

			}
		}
	}
}

// sendClientMsg used by the coach to send messaes to the client
func (s *Speed) sendClientMsg(value string) {
	select {
	case s.ClientMessagesChannel <- ClientMsg{value}:
	default:
		s.Log.Error(fmt.Errorf("client channel is full"), "not able to send client message", "value", value)
	}
}

// sendClientData is a generic function to send data to the client, generating error log in case of a full channel
func (s *Speed) sendClientData(ch chan<- float64, value float64) {
	select {
	case ch <- value:
	default:
		s.Log.Error(fmt.Errorf("client channel is full"), "not able to send client data", "value", value)
	}
}

// Calculator obtains the number of pull ups, the speed loss and the speed of the last pull up
// from the data passed by argument.
// Reset parameters is used to signal a new serie
// TODO autopause, detect pause when the climber stay still (or close to still) for several seconds
// Warn him the exercise has stopped in the ui
func (s *Speed) Calculator(data Data, reset bool) (numberPullUps *int, speedLoss *float64, lastSpeed *float64, maxSpeed *float64, cmd *BackendCmd) {
	// If we are starting a new set, restart all the values
	if reset {
		s.calculatorPullUpActive = false
		s.calculatorPullUpNumber = 0
		s.calculatorPullUpMaxSpeed = 0
		s.calculatorPullUpLastSpeed = 0
		s.calculatorMinDistance = 0
	}

	// Get the minimum position seen to use as the baseline to compare if a pull up has been started
	// Compare to zero used to check for a non initializated var (assuming the sensor will not give 0.0 never)
	if s.calculatorMinDistance == 0 || data.Position < s.calculatorMinDistance {
		s.calculatorMinDistance = data.Position
	}

	// Get higher point to decide when a pull up has finished
	if data.Position > s.calculatorMaxDistance {
		s.calculatorMaxDistance = data.Position
	}

	// If the position increments PullUpThresholdStart from the baseline, and the speed is positive,
	// the climber has started a pull up
	// TODO if the climber has to move more than PullUpThresholdStart from the position of start
	// the coach to the position to start the pull up, this function will not work.
	if !s.calculatorPullUpActive && data.Position > s.calculatorMinDistance+PullUpThresholdStart && data.Speed > 0 {
		s.calculatorPullUpActive = true

		// Reset the value of last speed, to measure the new pull up
		s.calculatorPullUpLastSpeed = 0

		// Check if this is the first pullup of a set
		if !s.exerciseActive {
			s.Log.V(3).Info("start event detected")

			// Start event
			c := "start"
			v := float64(data.Time.UnixNano())
			startCommand := BackendCmd{&c, &v}
			cmd = &startCommand
			s.exerciseActive = true
		}
	}

	// Detect end of exercise
	// Could be detected in the coach, if the climber stays still (don't generate new events), or here,
	// if the climer generate events within a small range, so near still
	if s.exerciseActive {
		s.calculatorLatestValues = append(s.calculatorLatestValues, data)
		max := 0.0
		min := math.Inf(1)
		lastSecondindex := 0
		now := time.Now()
		for i, v := range s.calculatorLatestValues {
			if v.Position > max {
				max = v.Position
			}
			if v.Position < min {
				min = v.Position
			}
			if now.Sub(v.Time) < 1*time.Second {
				lastSecondindex = i
			}
		}

		// End detected if the climber has moved in a small range in the last second
		difference := max - min
		if difference < EndExerciseDistanceThreshold && now.Sub(s.calculatorLatestValues[0].Time) > 1*time.Second {
			s.Log.V(3).Info("Exercise finished detection because only small movement",
				"threshold", EndExerciseTimeThreshold,
				"difference", difference,
				"first event used", s.calculatorLatestValues[0],
			)

			// End event
			c := "end"
			v := float64(data.Time.UnixNano())
			startCommand := BackendCmd{&c, &v}
			cmd = &startCommand
			s.exerciseActive = false
		}

		// Only stores last second events
		s.calculatorLatestValues = s.calculatorLatestValues[lastSecondindex:len(s.calculatorLatestValues)]
	}

	// A pull up is considered finished when the climber has descended PullUpThresholdEnd from the highest
	// point and the speed is negative
	if s.calculatorPullUpActive && data.Position < s.calculatorMaxDistance-PullUpThresholdEnd && data.Speed < 0 {
		s.calculatorPullUpNumber++
		s.calculatorPullUpActive = false
	}

	if s.calculatorPullUpActive {
		// Get max speed to calculate loss of speed in next pull ups
		if data.Speed > s.calculatorPullUpMaxSpeed {
			s.calculatorPullUpMaxSpeed = data.Speed
		}

		// Max speed of the pull up
		// TODO: maybe the speed data we need is not the max but the value in the propulsive phase? Or the mean value in that phase?
		// Sánchez-Medina, L. González-Badillo, J.J. (2010). Importance of the propulsive phase in strength assessment. Int J Sports Med. 31:123-129
		if data.Speed > s.calculatorPullUpLastSpeed {
			s.calculatorPullUpLastSpeed = data.Speed
		}
	}

	// Avoid dividing by zero
	sl := 0.0
	if s.calculatorPullUpMaxSpeed != 0 {
		sl = 1 - s.calculatorPullUpLastSpeed/s.calculatorPullUpMaxSpeed
	}
	speedLoss = &sl

	return &s.calculatorPullUpNumber, speedLoss, &s.calculatorPullUpLastSpeed, &s.calculatorPullUpMaxSpeed, cmd
}
