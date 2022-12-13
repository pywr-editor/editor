from pywr.recorders import Recorder


class NodePlusRecorder(Recorder):
    def __init__(self, *args, **kwargs):

        super(Recorder, self).__init__(*args, **kwargs)
