package strength

import (
	"fmt"
	"io"
	"os"
	"strconv"
	"time"
)

// Capture reads events from the device and send them to the channel
func (s *Strength) Capture(rawDataCh chan<- RawData) {
	s.Log.V(2).Info("start strength capture")

	// TODO: How to handle an error opening the device?
	loadCellFD, err := os.Open(s.Device)
	if err != nil {
		s.Log.Error(err, "Opening strength device")
		return
	}
	defer loadCellFD.Close()

	loadValueRaw := make([]byte, 15)
	var t time.Time

	for {
		valueSize, err := loadCellFD.Read(loadValueRaw)
		if err != nil {
			s.Log.Error(err, "reading from the load cell, ingoring this measure. Wait 1s to retry")
			time.Sleep(1 * time.Second)
			continue
		}
		t = time.Now()

		_, err = loadCellFD.Seek(0, io.SeekStart)
		if err != nil {
			s.Log.Error(err, "seeking to the start of the file")
		}

		// Only get the values readed except the new line
		load, err := strconv.ParseFloat(string(loadValueRaw[0:valueSize-1]), 64)
		if err != nil {
			s.Log.Error(err, "parsing cell load readings to float")
		}

		select {
		case rawDataCh <- RawData{load, t}:
		default:
			s.Log.Error(fmt.Errorf("rawData channel is full"), "not able to send data to processor")
		}

		// If this sleep is not set, it returns one value each 5ms and the
		// next value will come after 120ms
		// This sleeps averages the reads to ~25ms
		time.Sleep(time.Duration(s.GatherTime) * time.Millisecond)
	}
}
