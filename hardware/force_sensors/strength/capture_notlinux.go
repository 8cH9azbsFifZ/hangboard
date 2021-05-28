// +build !linux

package strength

// Capture reads events from the device and send them to the channel
// Not implemented for windows
func (s *Strength) Capture(rawDataCh chan<- RawData) {
}
