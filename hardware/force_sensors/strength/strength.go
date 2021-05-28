package strength

/*
* https://www.desnivel.com/escalada-roca/entrenamiento/analizando-la-importancia-de-la-fuerza-en-la-escalada/
* * measures:
*   - MVC: max voluntary contraction
*   - FTI: force-time integral
*   - RFD: rate of force development
* * types of workouts:
*   - MVC: for a predefined duration (7" for example), measure the strength. Metrics:
*     - average strength during the period
*     - max
*     - min
*     - deviation
*     - seconds left
*     - alarm when finished
*   - FTI, could be one serie or multiple series (repeaters)
*     - fti (integral force-time)
*     - duty cycle (percentage "on" vs "off")
*     - duration
*   - training:
*     - be able to set our MAX MCV and the percentage we want to train
*   - RFD:
*     - time to reach the max force (or 95? 99%?)
 */

import (
	"fmt"
	"math"
	"math/rand"
	"time"

	// TODO remove dependencies with speed package

	"github.com/go-logr/logr"
	"gonum.org/v1/gonum/integrate"
)

const (
	// LoadCellCalibrationFactor value to get readings in kg
	// TODO move this parameters to a settings file
	LoadCellCalibrationFactor = 0.0000628694
	// LoadCellOffset value to get 0kg when the cell is hanging
	LoadCellOffset = 8386793
	// StrengthCommandPause is the command to pause the gathering of data
	StrengthCommandPause Command = "pause"
	// StrengthCommandRestart is the command to restart the gathering of data
	StrengthCommandRestart Command = "restart"
	// StrengthCommandRestartNonStop start gathering data, deactivating auto stop detection
	StrengthCommandRestartNonStop Command = "restart_nonstop"
	// StrengthCommandTare is the command to put the position to zero
	StrengthCommandTare Command = "tare"
	// StrengthCommandCalibrate is the command to adjust the delta increments of movement
	StrengthCommandCalibrate Command = "calibrate"
	// StrengthCommandWeight stores the weight of the climber
	StrengthCommandWeight Command = "weight"
	// StrengthCommandSimulate gnerate random data simulating an exercise
	StrengthCommandSimulate Command = "simulate"
	// StartCommand message sent to the client with the real start time detected
	StartCommand Command = "start"
	// EndCommand message sent to the client with the real end time detected
	EndCommand Command = "end"
	// StrengthStartThreshold is the threshold used to decide a strength test is being done
	StrengthStartThreshold = 15.0
	// ClientChannelSize is the default size for channels sending data to the client
	ClientChannelSize = 10
	// Gravity value to convert from Kg to Newtons
	Gravity = 9.80665
	// TareMessage text send to the client when executed command "tare"
	TareMessage = "Tare done"
	// CalibrationMessage text send to the client when executed the command "calibration"
	CalibrationMessage = "Calibration done"
	// UnknownMessage is the prefix of the text send to the client when coach received an command unkown
	UnknownMessage = "Unkown command"
	// MeasuringMessage text send to the client to notify that the app has detected the start of the exercise
	MeasuringMessage = "Measuring..."
	// FinishedMessage text send to the client to notify that the app has detected the end of the exercise
	FinishedMessage = "Finished"
	// PausedMessage message send to the client when the app is not ready to run
	PausedMessage = "Pause"
	// StartMessage message send to the client when the app is ready to measure
	StartMessage = "Ready"
	// StartNonStopMessage message send to the client when the app is ready to measure without stop detection
	StartNonStopMessage = "ReadyNonStop"
	// LatestValueInterval is the lenght, in ms, of the latest data stored to make som calculations
	LatestValueInterval = 500
)

// Strength represents the structure to measure strength
type Strength struct {
	Log    logr.Logger
	Device string
	// ClientSampling defines how often should be sent data to the client
	ClientSampling time.Duration
	// ExportChannel used to share calculated data
	ExportChannel chan<- ExportData
	// ControlChannel pass commands from the client to the coach
	ControlChannel <-chan Control
	// ClientMessagesChannel used by the coach to send messages to the client
	ClientMessagesChannel chan<- ClientMsg
	// GatherTime is the expected time distance between points, in milliseconds
	GatherTime float64
	// BackendCmdChannel is used to signal client from start and end detection
	BackendCmdChannel chan<- BackendCmd

	// rawDataChannel pass data from the capturer to the processor
	rawDataChannel chan RawData
	// dataChannel pass data from the processor to the coach
	dataChannel chan Data

	// processorControlChannel used by the coach to control the processor
	processorControlChannel chan Control

	// Values used by the calculator to persist data between executions
	// calculatorLatestValues stores the latest values to be able to calculate correctly exercise parameters
	calculatorLatestValues []Data

	// calculatorExerciseStart marks the time when the exercise started
	calculatorExerciseStart time.Time
	// calculatorStrengthActive marks if a strength test is being done
	calculatorStrengthActive bool

	// calculatorMaxStrength is the max force applied during the test
	calculatorMaxStrength float64
	// calculatorAvgStrength is the slice of strength values while the exercise is being done, used to calculate the average
	calculatorActiveValues []Data

	// active defines if the coach is ready or not
	active bool

	// nonstop indicates to the calculator that it should deactivate auto stop detection
	// It is used for endurance exercises where the climber will release the force
	// for small periods during the exercise
	nonstop bool
}

// TODO clean unused structs
// Make private all not needed to be used outside

// RawData represents a reading from the load cell
// timeNs is the time, in nanoseconds
type RawData struct {
	value float64
	time  time.Time
}

// ClientMsg are the json messages passed to the client to notify things
// If the bell is on, when the message is received should make a sound
// TODO remove Bell, is being used? Move this channel to String?
// Use only this channel for commands response and anoter for the rest?
type ClientMsg struct {
	Value string
	Bell  bool
}

// Command are the available commands to send to the Coach
type Command string

// Control is used to receive commands from the client
type Control struct {
	Type  Command
	Value float64
}

// BackendCmd used to send commands to the client
// TODO refactor names to clarify usage
type BackendCmd struct {
	Command *string
	Value   *float64
}

// Data represents the useful data generated from each event
type Data struct {
	Strength float64
	Time     time.Time
	Interval time.Duration
}

// ExportData is the data exported to be used by the external APIs
type ExportData struct {
	// Time is elapsed time un seconds
	Time         *float64
	Strength     *float64
	MaxStrength  *float64
	AvgStrength  *float64
	StrengthLoss *float64
	RFD          *float64
	FTI          *float64
}

// RunStrength starts the goroutines to measure and process speed
func (s *Strength) RunStrength() {
	s.Log.V(2).Info("start strength")

	// TODO cuanto espacio poner en estos canales?
	s.rawDataChannel = make(chan RawData, 10)
	s.dataChannel = make(chan Data, 10)
	s.processorControlChannel = make(chan Control, 10)

	numberOfPreviousValuesStored := int(LatestValueInterval / s.GatherTime)
	s.calculatorLatestValues = make([]Data, numberOfPreviousValuesStored)

	go s.Capture(s.rawDataChannel)
	go s.Process(s.rawDataChannel, s.processorControlChannel, s.dataChannel)
	go s.Coach(s.dataChannel, s.ControlChannel, s.processorControlChannel)
}

// Process get raw events and calculate strength.
// Send the data to the coach
// Could be controlled by the coach (to pause, reset, etc)
func (s *Strength) Process(rawDataCh <-chan RawData, procControlCh <-chan Control, dataCh chan<- Data) {
	s.Log.V(2).Info("start strength process")

	// variables to calibrate readings
	var strength float64
	var offset float64 = LoadCellOffset
	calibrationFactor := LoadCellCalibrationFactor

	// Used to calculate the time used to get reads
	lastReadTime := time.Now()
	var readTime time.Duration

	// Control if generated data should be sent to the encoderData channel
	// Wait for the restart command to start sending data to the coach
	sendEvents := false

	for {
		select {
		// TODO remove coach commands that should not be here
		case c := <-procControlCh:
			s.Log.V(4).Info("process command", "value", c)
			switch c.Type {
			case StrengthCommandPause:
				sendEvents = false
			case StrengthCommandRestart:
				sendEvents = true
			case StrengthCommandTare:
				offset += strength
				s.Log.V(3).Info("tare command", "offset", offset)
			case StrengthCommandCalibrate:
				// c.Value is the % to increse/decrease
				calibrationFactor *= (1 + c.Value/100)
				s.Log.V(3).Info("calibrate", "value", c.Value, "calibrationFactor", calibrationFactor)
			}

		case e := <-rawDataCh:
			s.Log.V(4).Info("process load cell", "value", e.value, "time", e.time)
			strength = (e.value - offset) * calibrationFactor

			readTime = e.time.Sub(lastReadTime)
			lastReadTime = e.time

			if sendEvents {
				// Send data without blocking. Let the processor run if the client or db queues are full
				select {
				case dataCh <- Data{strength, e.time, readTime}:
					s.Log.V(5).Info("sent processed strength to coach", "strength", strength)
				default:
					s.Log.Error(fmt.Errorf("coach channel is full"), "not able to send data", "strength", strength)
				}
			}
		}
	}
}

// Coach get the data processed and calculates useful info for the client
// dataCh should be receive only, but we send data on it with the simulation command
func (s *Strength) Coach(dataCh chan Data, controlCh <-chan Control, processorControlCh chan<- Control) {

	// Defines if coach is working. Set by the client with commands
	s.active = false
	// Used to signal the calculator to reset to initial state
	reset := false

	// Store the last time a value was pushed to the client
	var previousSent time.Time
	// Uniq identifier for each of the metric sent
	var id int

	for {
		select {
		// Handle commands
		// TODO add sampling command to be able to increase/reduce the speed of sampling, modifying s.GatherTime
		case c := <-controlCh:
			s.Log.V(3).Info("coach command", "cmd", c.Type)
			switch c.Type {
			case StrengthCommandPause:
				// TODO refactor how to handle pause?
				// Now go is detecting the end, notifying the frontend and the frontend sending
				// back a command to pause
				// Maybe it has sense, as it is the UI which have to decide what to do
				s.active = false

				// Stop the calculator and clean data
				s.calculatorStrengthActive = false
				s.calculatorLatestValues = s.calculatorLatestValues[:0]

				// Pause the gather of metrics
				processorControlCh <- c
				msg := ClientMsg{PausedMessage, false}
				err := s.sendClientMsg(msg)
				if err != nil {
					s.Log.Error(err, "sending message to client", "msg", msg)
				}
			case StrengthCommandRestart:
				s.active = true
				// Reset signal to calculator
				reset = true
				// Restart the gather of metrics
				processorControlCh <- c
				msg := ClientMsg{StartMessage, false}
				err := s.sendClientMsg(msg)
				if err != nil {
					s.Log.Error(err, "sending message to client", "msg", msg)
				}
			case StrengthCommandRestartNonStop:
				s.active = true
				s.nonstop = true
				// Reset signal to calculator
				reset = true
				// Restart the gather of metrics
				c.Type = StrengthCommandRestart
				processorControlCh <- c
				msg := ClientMsg{StartNonStopMessage, false}
				err := s.sendClientMsg(msg)
				if err != nil {
					s.Log.Error(err, "sending message to client", "msg", msg)
				}
			case StrengthCommandTare:
				// Just send the command to the processor
				processorControlCh <- c
				msg := ClientMsg{TareMessage, false}
				err := s.sendClientMsg(msg)
				if err != nil {
					s.Log.Error(err, "sending message to client", "msg", msg)
				}
			case StrengthCommandCalibrate:
				// Just send the command to the processor
				processorControlCh <- c
				msg := ClientMsg{CalibrationMessage, false}
				err := s.sendClientMsg(msg)
				if err != nil {
					s.Log.Error(err, "sending message to client", "msg", msg)
				}
			case StrengthCommandSimulate:
				msg := ClientMsg{"Simulation start", false}
				err := s.sendClientMsg(msg)
				if err != nil {
					s.Log.Error(err, "sending message to client", "msg", msg)
				}
				// Pause the generator
				processorControlCh <- Control{StrengthCommandPause, 0}

				// Generate random values
				go func() {
					rand.Seed(time.Now().UnixNano())
					maxForce := 50 + rand.Float64()*30
					startDuration := time.Duration(rand.Intn(300))*time.Millisecond + 100*time.Millisecond
					duration := time.Duration(rand.Intn(7))*time.Second + 3*time.Second
					endDuration := time.Duration(rand.Intn(300))*time.Millisecond + 100*time.Millisecond
					loss := float64(rand.Intn(25)) / 100.0
					step := 20 * time.Millisecond
					s.Log.V(3).Info("Strength simulator",
						"maxForce", maxForce,
						"startDuration", startDuration.Seconds(),
						"duration", duration.Seconds(),
						"endDuration", endDuration.Seconds(),
						"loss", loss,
						"step", step.Seconds(),
					)

					// Increasing force
					for i := 0; i < int(startDuration/step); i++ {
						dataCh <- Data{
							float64(i) * maxForce / float64(startDuration/step),
							time.Now(),
							time.Duration(20 * time.Millisecond),
						}
						time.Sleep(20 * time.Millisecond)
					}

					// Steady force
					for i := 0; i < int(duration/step); i++ {
						dataCh <- Data{
							maxForce - float64(i)*maxForce*loss/float64(duration/step),
							time.Now(),
							time.Duration(20 * time.Millisecond),
						}
						time.Sleep(20 * time.Millisecond)
					}

					// Decreasing force
					for i := 0; i < int(endDuration/step); i++ {
						dataCh <- Data{
							maxForce*loss/float64(duration/step) - float64(i)*maxForce*loss/float64(endDuration/step),
							time.Now(),
							time.Duration(20 * time.Millisecond),
						}
						time.Sleep(20 * time.Millisecond)
					}
					s.Log.V(3).Info("Strength simulator end")
				}()
			default:
				s.Log.Error(fmt.Errorf("unkown command"), "coach", "type", c.Type)
				text := fmt.Sprintf("%s: %s", UnknownMessage, c.Type)
				msg := ClientMsg{text, false}
				err := s.sendClientMsg(msg)
				if err != nil {
					s.Log.Error(err, "sending message to client", "msg", msg)
				}
			}

		// Handle new data
		case d := <-dataCh:
			// Only process new data if it is active
			if s.active {
				exerciseDuration, maxStrength, avgStrength, strengthLoss, rfd, fti, dutyCycle, controlCmd := s.Calculator(d, reset)
				reset = false

				s.Log.V(4).Info("send data to client",
					"strength", d.Strength,
					"exerciseDuration", exerciseDuration.Seconds(),
					"maxStrength", maxStrength,
					"avgStrength", avgStrength,
					"strengthLoss", strengthLoss,
					"rfd", rfd,
					"fti", fti,
					"dutyCucle", dutyCycle,
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

				duration := float64(exerciseDuration.Seconds())
				strength := d.Strength

				select {
				case s.ExportChannel <- ExportData{
					Time:         &duration,
					Strength:     &strength,
					MaxStrength:  maxStrength,
					AvgStrength:  avgStrength,
					StrengthLoss: strengthLoss,
					RFD:          rfd,
					FTI:          fti,
				}:
				default:
					s.Log.Error(fmt.Errorf("channel full"), "Cannot send data", "channel", "ExportData")
				}
			}
		}
	}
}

// sendClientMsg used by the coach to send messages to the client
func (s *Strength) sendClientMsg(value ClientMsg) error {
	s.Log.V(3).Info("Send message to client", "msg", value)
	select {
	case s.ClientMessagesChannel <- value:
	default:
		return fmt.Errorf("client channel is full")
	}
	return nil
}

// Calculator get the strength data from the sensor and calculate all the values needed by the coach
// Reset parameters is used to signal a new serie
// Pointer values could be null if they are not yet available
// strengthLoss is the loss of strength in percentage (0-100)
func (s *Strength) Calculator(data Data, reset bool) (exerciseDuration time.Duration, maxStrength *float64, avgStrength *float64, strengthLoss *float64, rfd *float64, fti *float64, dutyCycle *float64, cmd *BackendCmd) {
	if reset {
		s.calculatorLatestValues = s.calculatorLatestValues[:0]
		s.calculatorActiveValues = s.calculatorActiveValues[:0]
		s.calculatorMaxStrength = 0
	}

	// Store the latest numberOfPreviousValuesStored of values
	s.calculatorLatestValues = append(s.calculatorLatestValues, data)

	// NumberOfPreviousValuesStored is the size of the slice to store recent values
	numberOfPreviousValuesStored := int(LatestValueInterval / s.GatherTime)
	if numberOfPreviousValuesStored != 0 && len(s.calculatorLatestValues) > numberOfPreviousValuesStored {
		// Removes the oldest value
		// TODO change the expresion to: s.calculatorLatestValues[len(s.calculatorLatestValues)-numberOfPreviousValuesStored:len(numberOfPreviousValuesStored)] ?
		s.calculatorLatestValues = s.calculatorLatestValues[1:numberOfPreviousValuesStored]
	}

	if !s.calculatorStrengthActive {
		start, positionRealStart := s.calculateStart()
		// Starting the exercise
		if start {
			s.calculatorStrengthActive = true
			s.calculatorExerciseStart = s.calculatorLatestValues[positionRealStart].Time

			// Add to the slice of active values all the data from the real start of the exercise, except the last point, that will be added later
			// Empty active values slice if the calculated start is the same as the last value
			positionOfLastValue := len(s.calculatorLatestValues) - 2
			if positionRealStart < positionOfLastValue {
				s.calculatorActiveValues = s.calculatorLatestValues[positionRealStart:positionOfLastValue]
			} else {
				s.calculatorActiveValues = s.calculatorActiveValues[:0]
			}

			// TODO probably this should not be here and should be the coach the responsible of handling this message
			// TODO are we using this? remove?
			//s.sendClientMsg(ClientMsg{MeasuringMessage, false})
			//
			s.Log.V(3).Info("start event detected")

			c := "start"
			v := float64(s.calculatorExerciseStart.UnixNano())
			startCommand := BackendCmd{&c, &v}
			cmd = &startCommand
		}
	} else {
		// If the exercise is being done, calculate data
		//
		// Decides that the exercise has finished
		end, positionRealEnd := s.calculateEnd()
		// Ending the exercise and run the last round of measures
		if end {
			// Correct the calculatorActiveValues, removing values after the real end
			s.calculatorActiveValues = s.calculatorActiveValues[0:positionRealEnd]

			// TODO probably this should not be here and should be the coach the responsible of handling this message
			// TODO are we using this? remove?
			//s.sendClientMsg(ClientMsg{FinishedMessage, false})

			s.Log.V(3).Info("end event detected")

			realEndTime := s.calculatorActiveValues[positionRealEnd-1].Time
			c := "end"
			v := float64(realEndTime.UnixNano()) / 1e9
			endCommand := BackendCmd{&c, &v}
			// TODO check start end end commands are being sent twice and after end, it send another
			// two starts and two ends
			cmd = &endCommand
		} else {
			s.calculatorActiveValues = append(s.calculatorActiveValues, data)
		}

		if data.Strength > s.calculatorMaxStrength {
			s.calculatorMaxStrength = data.Strength
		}

		// "data" could be invalid as we have finished and that value is after the real end
		// Use this value as is the last valid value after real end reconfiguration
		lastValidData := s.calculatorActiveValues[len(s.calculatorActiveValues)-1]

		exerciseDuration = lastValidData.Time.Sub(s.calculatorExerciseStart)
		maxStrength = &s.calculatorMaxStrength
		as := AverageStrength(s.calculatorActiveValues, s.nonstop)
		avgStrength = &as

		sl := 100 - (100 * lastValidData.Strength / *maxStrength)
		strengthLoss = &sl

		r := RFD(s.calculatorActiveValues)
		rfd = &r

		// Calculate FTI only if we have enough values (gonum restriction)
		// Not normalized
		if len(s.calculatorActiveValues) >= 3 {
			f := FTI(s.calculatorActiveValues)
			fti = &f
		}
		// This should return the real duty cycle vs the programmed one
		d := DutyCycle(s.calculatorActiveValues)
		dutyCycle = &d
	}

	return
}

// DutyCycle calculate the percentage of time doing force vs resting
// It decides when it's "on" and when "off" based on the StrengthStartThreshold
func DutyCycle(data []Data) float64 {
	// TODO: it is worth it?
	return 0
}

// RFD the highest positive value from the first derivative of the force signal (kg/s)
// https://journals.lww.com/nsca-jscr/Fulltext/2013/02000/Differences_in_Climbing_Specific_Strength_Between.5.aspx
func RFD(data []Data) float64 {
	max := 0.0
	firstDerivateData := Derivate(data)
	for _, d := range firstDerivateData {
		if d > max {
			max = d
		}
	}
	return max
}

// Derivate calculates the discrete derivative for an slice of StrengthData values
func Derivate(data []Data) []float64 {
	res := []float64{}
	for i := 1; i < len(data); i++ {
		df := data[i].Strength - data[i-1].Strength
		dt := data[i].Time.Sub(data[i-1].Time)
		res = append(res, df/float64(dt.Seconds()))
	}
	return res
}

// Difference calculate the difference between values of a slice of float64 values
func Difference(data []float64) []float64 {
	res := []float64{}
	for i := 1; i < len(data); i++ {
		res = append(res, data[i]-data[i-1])
	}
	return res
}

// FirstThresholdCross return the position of the first value crossing, or matching, the threshold,
// in absolute values
func FirstThresholdCross(data []float64, threshold float64) (int, error) {
	for k, v := range data {
		if math.Abs(v) >= math.Abs(threshold) {
			return k, nil
		}
	}
	return 0, fmt.Errorf("no value crossed the threshold")
}

// MovingAverage returns the moving average of blocks of n items
func MovingAverage(data []float64, n int) (res []float64) {
	for i := 1; i <= len(data); i++ {
		backCount := i - n
		if backCount < 0 {
			backCount = 0
		}

		res = append(res, Average(data[backCount:i]))
	}

	return
}

// Average return the average value of a slice of float64 values
func Average(data []float64) float64 {
	sum := 0.0
	for _, v := range data {
		sum += v
	}
	return sum / float64(len(data))
}

// FTI calculate the integraf force-time from a serie of StrengthData values
// Return value is expressed in Newton*second
func FTI(data []Data) float64 {
	fx := []float64{}
	x := []float64{}

	for _, v := range data {
		// Convert mass to newtons
		fx = append(fx, v.Strength*Gravity)
		// Convert time to unix epoch float64
		x = append(x, float64(v.Time.UnixNano())/1e9)
	}

	return integrate.Simpsons(x, fx)
}

// calculateStart decides, based on the latest values, when the strength test has started.
// To make this calculation less error prone, this function could not detect the start of the exercise in the precise moment it starts,
// and will wait to more measures to come to be accurate.
// This is the reason to also return the position of the slice of latest values when the exercise really started
// TODO this method is not going to be useful to measure RFD, because we are considering the start time later than the real start
// Now it always return the latest value as the real start
//
// How to detect a new exercise has started
// To get a good value for RFD and FTI we need to know the exact start time.
// The climber could load the cell while preparing or even have some load in the cell before starting
// We could store the previous 500ms of values and when we detect a high load, indicating the exercise has begin, go back in time to
// get the exact start time
func (s *Strength) calculateStart() (bool, int) {
	// Calculate the average over the lat 5 values, or the total of values of there are less than five
	lastValues := len(s.calculatorLatestValues) - 5
	if lastValues < 0 {
		lastValues = 0
	}

	if AverageStrength(s.calculatorLatestValues[lastValues:], false) > StrengthStartThreshold {
		realStartPosition := len(s.calculatorLatestValues) - 1
		s.Log.V(3).Info("start exercise", "real start", s.calculatorLatestValues[realStartPosition].Time, "strength", s.calculatorLatestValues[realStartPosition].Strength)
		return true, realStartPosition
	}
	return false, 0
}

// calculateEnd decides when the exercise has finished, based on a big drop of force
// The real end is when the climber started to release the force. Is an index number relative to the s.calculatorActiveValues
// TODO improve this function. Too confusing
// TODO how to handle repeaters? How to differenciate finished from rest? Maybe need a command from the client
func (s *Strength) calculateEnd() (bool, int) {
	// If we are in NonStop mode, automatic detection is disabled
	if s.nonstop {
		return false, 0
	}

	// If it has no data, it has not finished
	// Could not finish if we do not have at least two values
	if len(s.calculatorActiveValues) <= 2 {
		return false, 0
	}

	// Use the average of the latest 5 points (or less, if we don't have enough) to decide if the force
	// has crossed the threshold to consider the exercise finished
	startIndex := 0
	if len(s.calculatorActiveValues) >= 5 {
		startIndex = len(s.calculatorActiveValues) - 5
	}

	// TODO remove this threshold detect and use only the derivate?
	// With threshold, we are sending "erroneous" data to the client before we
	// detect the real end
	if AverageStrength(s.calculatorActiveValues[startIndex:], false) < StrengthStartThreshold {
		// Once we have detected a big drop on the values, we use de derivative to find
		// when does it started.
		// We use the last 500ms
		// TODO if the climber releases the force slowly, we won't detect the finish
		backPositions := int(500 / s.GatherTime)
		if backPositions > len(s.calculatorActiveValues) {
			backPositions = len(s.calculatorActiveValues) - 1
		}

		startIndex = len(s.calculatorActiveValues) - backPositions
		d := Derivate(s.calculatorActiveValues[startIndex:])

		// Smooth the values
		// TODO try to use this values to calculate end
		/*
			dMovAvg := MovingAverage(d, int(backPositions/10))
			s.Log.V(1).Info("End, moving average", "dMovAvg", dMovAvg)
		*/

		// Get the first value higher than the average of diff values
		n, err := FirstThresholdCross(d, Average(d))
		if err != nil {
			// An error could happend if there is not enough values, but que filter at the beggining
			// of the function should return if there is not enough values
			return false, 0
		}

		// n is the position in the "d" slice with a value higher than the average
		// The "d" slice have one element less than the slice passed as the parameter.
		// So, a position i in the "d" slice means the value we are looking for is i+1 in
		// the values slice, but value is the first big drop, so we skip it
		endIndex := startIndex + n

		realEndTime := s.calculatorActiveValues[endIndex]
		s.Log.V(3).Info("end exercise", "real end", realEndTime)

		return true, endIndex

		/*
			// Smooth the values
			dMovAvg := MovingAverage(d, int(backPositions/10))

			// Get the array of value diferences of the averaged values
			dif := Difference(dMovAvg[int(backPositions/10):len(dMovAvg)])
			s.Log.V(1).Info("End, diferences", "dif", dif)


			// n is the position of the "dif" slice crossing the average

			s.Log.V(1).Info("", "dd", dd)

			realEndTime := s.calculatorActiveValues[len(s.calculatorActiveValues)-1].Time
			s.Log.V(3).Info("end exercise", "real end", realEndTime)

			return true, len(s.calculatorActiveValues) - 1
		*/
	}
	return false, 0
}

// AverageStrength calculate the average of a slice of Data values
// nonstop param decides if small values should be ignored
func AverageStrength(data []Data, nonstop bool) float64 {
	sum := 0.0
	ignoredValues := 0
	for _, v := range data {
		// In NonStop mode, don't use small values to compute the average
		// TODO improve this using the end event detection?
		if nonstop && v.Strength < StrengthStartThreshold {
			ignoredValues++
			continue
		}
		sum += v.Strength
	}
	return sum / float64(len(data)-ignoredValues)
}
