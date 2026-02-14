class jparse:    
    @property
    def experimentList(self):
        return self._experimentList
    
    @property
    def parsedData(self):
        return self._parsedData
    
    @property
    def data(self):
        return self._data
    
    def __init__(self, filename_list):
        # filename_list is expected to be an iterable of paths
        self._methodType = MethodType()
        self._experimentList = []
        self.files = []
        self.experimentToFileMap = {}
        self._parsedData = self._parse(filename_list)
        self.experimentIndex = 0
        self._data = self._simplify()
        
    def _parse(self, filenames):
        # takes in the files
        # parses the raw data to an object
        # simplifies the values and adds it to the 'data' object
        
        self._getFilenames(filenames)
        
        try:
            index = 0
            readData = {}
            for filename in filenames:
                f = open(filename, "rb")
                readData[self.files[index]] = (
                    f.read()
                     .decode('utf-16')
                     .replace('\r\n', ' ')
                     .replace(':true', r':"True"')
                     .replace(':false', r':"False"')
                )
                index = index + 1
                f.close()
        except Exception as e:
            print('Could not find or open file: ' + str(filename), e)
            return
            
        try:
            parsedData = {}
            for file in self.files:
                # has a weird character at the end
                data2 = readData[file][0:(len(readData[file]) - 1)]
                # parse to nested dicts
                parsedData[file] = json.loads(data2)
        except Exception as e:
            print('Failed to parse string to JSON', e)
            return
        
        try:
            for file in self.files:
                # DEBUG: see what keys exist
                print("Top-level keys in", file, ":", parsedData[file].keys())
                if 'measurements' not in parsedData[file]:
                    print("No 'measurements' key in", file)
                    continue
                for measurement in parsedData[file]['measurements']:
                    currentMethod = self._getMethodType(measurement.get('method', ''))
                    currentMethod = currentMethod.upper()
                    index = len(
                        [i for i, s in enumerate(self._experimentList)
                         if currentMethod in s]
                    )
                    self._experimentList.append(currentMethod + ' ' + str(index + 1))
        except Exception as e:
            print("Failed to generate property: experimentList 'measurements'", e)
            return

        return parsedData
    
    def _simplify(self):
        simplifiedData = {}
        experimentIndex = 0
        for file in self.files:
            rawData = self._parsedData[file]
            if 'measurements' not in rawData:
                print("No 'measurements' key in rawData for", file)
                continue
            for measurement in rawData['measurements']:
                currentMethod = self._getMethodType(measurement.get('method', ''))
                currentMethod = currentMethod.upper()
                if currentMethod in self._methodType.SWV or currentMethod in self._methodType.CV:
                    simplifiedData[self._experimentList[experimentIndex]] = self._getXYDataPoints(measurement)
                    simplifiedData[self._experimentList[experimentIndex] + ' Details'] = self._getXYUnits(measurement)
                if currentMethod in self._methodType.EIS:
                    simplifiedData[self._experimentList[experimentIndex]] = self._getEISDataPoints(measurement)
                self.experimentToFileMap[self._experimentList[experimentIndex]] = file
                experimentIndex = experimentIndex + 1
        return simplifiedData

    def _getFilenames(self, files):
        for f in files:
            parts = f.split('\\')
            name = parts[len(parts) - 1].replace('.pssession', '')
            self.files.append(name)
                
    def _getMethodType(self, method):
        methodName = ''
        splitted = method.split("\r\n")
        for line in splitted:
            if "METHOD_ID" in line:
                methodName = line.split("=")[1]
        return methodName

