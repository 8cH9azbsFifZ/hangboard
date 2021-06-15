// +build !linux

package speed

// Capture reads events from the device and send them to the channel
func (s *Speed) Capture(rawDataCh chan<- EncoderRawData) {
}
