

    def run_one_measure(self):
        self._TimeCurrent = time.time()

        self.sensor_hangdetector.run_one_measure()
        
        self._detect_hang_state_change()
        self._measure_hangtime()
        self._measure_additional_parameters()
        #logging.debug(" Hang load " + str(self.MaximalLoad))

       
    

