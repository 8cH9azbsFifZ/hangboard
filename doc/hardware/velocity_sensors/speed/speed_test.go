package speed

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strconv"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// TestData represents the JSON file with the simulation data
type TestData struct {
	Data struct {
		Result []struct {
			Metric struct {
				Name string `json:"__name__"`
			} `json:"metric"`
			Values [][]interface{} `json:"values"`
		} `json:"result"`
		ResultType string `json:"resultType"`
	} `json:"data"`
	Status string `json:"status"`
}

// ParseJSONTestData generate an array of data points from a .json file
// with measures of speed and position
func ParseJSONTestData(file string) []Data {
	fileRead, err := ioutil.ReadFile(file)
	if err != nil {
		panic(fmt.Sprintf("reading test data file %s: %v", file, err))
	}

	var testData TestData
	err = json.Unmarshal(fileRead, &testData)
	if err != nil {
		panic(fmt.Sprintf("test data file unmarshal %s: %v", file, err))
	}

	data := []Data{}
	result := testData.SpeedData.Result[0]
	for i, r := range result.Values {
		v0, err := strconv.ParseFloat(r[1].(string), 64)
		if err != nil {
			panic(fmt.Sprintf("parsing speed value '%s': %v", r[1], err))
		}

		v1, err := strconv.ParseFloat(testData.SpeedData.Result[1].Values[i][1].(string), 64)
		if err != nil {
			panic(fmt.Sprintf("parsing position value '%s': %v", testData.SpeedData.Result[1].Values[i][1], err))
		}

		t, ok := r[0].(float64)
		if !ok {
			panic(fmt.Sprintf("parsing epoch '%s' to float64", r[0]))
		}

		// Do not assume which value comes first in the json data
		// case encoder_speed_value
		speed := v0
		position := v1
		if result.Metric.Name == "encoder_position_value" {
			speed = v1
			position = v0
		}

		data = append(data, Data{
			Position: position,
			Speed:    speed,
			// Convert a float64 value to epoch in sec and the ns part of the epoch
			Time: time.Unix(int64(t), int64((t-float64(int64(t)))*1e9)),
		})
	}

	return data
}

func TestCalculator(t *testing.T) {
	tests := []struct {
		name                  string
		data                  []Data
		expectedNumberPullUps int
		expectedSpeedLoss     float64
		expectedLastSpeed     float64
		expectedMaxSpeed      float64
	}{
		{
			name: "zero",
			data: []Data{
				Data{Position: 0, Speed: 0, Time: time.Unix(0, 0)},
			},
			expectedNumberPullUps: 0,
			expectedSpeedLoss:     0,
			expectedLastSpeed:     0,
			expectedMaxSpeed:      0,
		},
		{
			name:                  "two pull ups",
			data:                  ParseJSONTestData("tests/two_pull_ups/data.json"),
			expectedNumberPullUps: 2,
			expectedSpeedLoss:     0,
			// The last pull up was the fastest
			expectedLastSpeed: 1.308518248175,
			expectedMaxSpeed:  1.308518248175,
		},
		{
			name:                  "four pull ups",
			data:                  ParseJSONTestData("tests/four_pull_ups/data.json"),
			expectedNumberPullUps: 4,
			expectedSpeedLoss:     0.1176825588414715,
			expectedLastSpeed:     1.081876885938,
			expectedMaxSpeed:      1.226176470588,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			speed := Speed{}
			var numberPullUps int
			var speedLoss float64
			var lastSpeed float64
			var maxSpeed float64

			for _, d := range test.data {
				numberPullUps, speedLoss, lastSpeed, maxSpeed = speed.Calculator(d, false)
			}
			assert.Equal(t, test.expectedNumberPullUps, numberPullUps, "pull up number")
			assert.Equal(t, test.expectedSpeedLoss, speedLoss, "speed loss")
			assert.Equal(t, test.expectedLastSpeed, lastSpeed, "last speed")
			assert.Equal(t, test.expectedMaxSpeed, maxSpeed, "max speed")
		})
	}
}
