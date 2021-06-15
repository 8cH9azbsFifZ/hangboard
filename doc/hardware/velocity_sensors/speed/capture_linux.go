package speed

import (
	"fmt"
	"time"

	evdev "github.com/gvalkov/golang-evdev"
)

// Capture reads events from the device and send them to the channel
func (s *Speed) Capture(rawDataCh chan<- EncoderRawData) {
	s.Log.V(3).Info("start speed capture")

	// TODO: better handle of device file "reconnect"
	// Something to open the file when it cames to existance, without having to poll?
	var device *evdev.InputDevice
	var err error
	for {
		device, err = evdev.Open(s.Device)
		if err != nil {
			s.Log.V(4).Info("opening device, wait 1s", "device", s.Device, "error", err)
			time.Sleep(1 * time.Second)
		} else {
			break
		}
	}

	for {
		events, err := device.Read()
		if err != nil {
			s.Log.Error(err, "error reading from device encoder")
			err := device.Release()
			if err != nil {
				s.Log.Error(err, "releasing device after incorrect reading")
			}

			// Try to open the file again
			for {
				s.Log.V(5).Info("trying to open the file again")
				device, err = evdev.Open(s.Device)
				if err == nil {
					s.Log.V(3).Info("device opened again")
					break
				}
				time.Sleep(1 * time.Second)
			}
			continue
		}

		s.Log.V(5).Info("new events from linear encoder", "events", events)
		for i := range events {
			event := &events[i]
			if event.Type == evdev.EV_REL {
				select {
				case rawDataCh <- EncoderRawData{event.Value, event.Time.Nano()}:
				default:
					s.Log.Error(fmt.Errorf("rawData channel is full"), "not able to send data to processor")
				}
			}
		}
	}
}
