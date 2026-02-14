# -*- coding: utf-8 -*-
"""
Modified on 13 Feb
@author: Stephan, Russell
"""

import json  # built-in instead of simplejson


class Description:
    __slots__ = ['SWVParameters', 'CVParameters', 'Pretreatment', 'Technique']
    
    def __init__(self):
        self.SWVParameters = ''
        self.CVParameters = ''
        self.Pretreatment = ''
        self.Technique = ''


class Unit:
    __slots__ = ['type', 's', 'c', 't', 'q', 'a']
    
    def __init__(self):
        self.type = ''
        self.s = ''
        self.c = ''
        self.t = ''
        self.q = ''
        self.a = ''


class Datavalue:
    __slots__ = ['v', 's', 'c', 't']
    
    def __init__(self):
        self.v = 0.0
        self.s = 0
        self.c = 0
        self.t = ''


class Dataset:
    __slots__ = ['type', 'values']
    
    def __init__(self):
        self.type = ''
        self.values = []


class Appearance:
    __slots__ = ['type', 'autoassigncolor', 'color', 'linewidth',
                 'symbolsize', 'symboltype', 'symbolfill', 'noline']
    
    def __init__(self):
        self.type = ''
        self.autoassigncolor = False
        self.color = ''
        self.linewidth = 0
        self.symbolsize = 0
        self.symboltype = 0
        self.symbolfill = False
        self.noline = False


class Eisdatalist:
    __slots__ = ['appearance', 'title', 'hash', 'scantype',
                 'freqtype', 'cdc', 'fitvalues', 'dataset']
    
    def __init__(self):
        self.appearance = Appearance()
        self.title = ''
        self.hash = []
        self.scantype = 0
        self.freqtype = 0
        self.cdc = object()
        self.fitvalues = object()
        self.dataset = Dataset()


class Value:
    __slots__ = ['type', 'arraytype', 'description', 'unit', 'datavalues', 'datavaluetype']
    
    def __init__(self):
        self.type = ''
        self.arraytype = 0
        self.description = ''
        self.unit = Unit()
        self.datavalues = []
        self.datavaluetype = ''


class Peaklist:
    __slots__ = ['peaktype', 'left', 'right', 'peak', 'isign']
    
    def __init__(self):
        self.peaktype = 0
        self.left = 0
        self.right = 0
        self.peak = 0
        self.isign = 0


class Xaxisdataarray:
    __slots__ = ['type', 'arraytype', 'description', 'unit', 'datavalues', 'datavaluetype']
    
    def __init__(self):
        self.type = ''
        self.arraytype = 0
        self.description = ''
        self.unit = Unit()
        self.datavalues = []
        self.datavaluetype = ''


class Yaxisdataarray:
    __slots__ = ['type', 'arraytype', 'description', 'unit', 'datavalues', 'datavaluetype']
    
    def __init__(self):
        self.type = ''
        self.arraytype = 0
        self.description = ''
        self.unit = Unit()
        self.datavalues = []
        self.datavaluetype = ''


class Curve:
    __slots__ = ['appearance', 'title', 'hash', 'type', 'xaxis', 'yaxis',
                 'xaxisdataarray', 'yaxisdataarray', 'meastype', 'peaklist',
                 'corrosionbutlervolmer', 'corrosiontafel']
    
    def __init__(self):
        self.appearance = Appearance()
        self.title = ''
        self.hash = []
        self.type = ''
        self.xaxis = 0
        self.yaxis = 0
        self.xaxisdataarray = Xaxisdataarray()
        self.yaxisdataarray = Yaxisdataarray()
        self.meastype = 0
        self.peaklist = []
        self.corrosionbutlervolmer = []
        self.corrosiontafel = []


class Measurement:
    __slots__ = ['title', 'timestamp', 'utctimestamp', 'deviceused', 'deviceserial',
                 'devicefw', 'type', 'dataset', 'method', 'curves', 'eisdatalist']
    
    def __init__(self):
        self.title = ''
        self.timestamp = object()
        self.utctimestamp = object()
        self.deviceused = 0
        self.deviceserial = ''
        self.devicefw = ''
        self.type = ''
        self.dataset = Dataset()
        self.method = ''
        self.curves = []
        self.eisdatalist = []


class Data:
    __slots__ = ['type', 'coreversion', 'methodformeasurement', 'measurements']
    
    def __init__(self):
        self.type = ''
        self.coreversion = ''
        self.methodformeasurement = ''
        self.measurements = []


class MethodType:
    __slots__ = ['CV', 'SWV', 'EIS']
    
    def __init__(self):    
        self.CV = 'CV'
        self.SWV = 'SWV'
        self.EIS = 'EIS'


class axis:
    __slots__ = ['xvalues', 'yvalues']
    
    def __init__(self):
        self.xvalues = []
        self.yvalues = []


class EISMeasurement:
    __slots__ = ['freq', 'zdash', 'potential', 'zdashneg', 'Z', 'phase', 'current',
                 'npoints', 'tint', 'ymean', 'debugtext', 'Y', 'YRe', 'YIm',
                 'scale', 'Cdash', 'Cdashdash']
    
    def __init__(self):
        self.freq = []
        self.zdash = []
        self.potential = []
        self.zdashneg = []
        self.Z = []
        self.phase = []
        self.current = []
        self.npoints = []
        self.tint = []
        self.ymean = []
        self.debugtext = []
        self.Y = []
        self.YRe = []
        self.YIm = []
        self.Cdash = []
        self.Cdashdash = []
        self.scale = 100000  # standard set to mega ohms


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
        # simplifies the values and adds it to
