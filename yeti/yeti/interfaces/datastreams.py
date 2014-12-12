from ..context import get_context

context_datastore_key = "datastreams"


def get_datastream(dsid):
    context = get_context()
    datastreams_data = context.get_interface_data(context_datastore_key)[0]
    if dsid not in datastreams_data:
        datastreams_data[dsid] = Datastream()
    return datastreams_data[dsid]


class Datastream(object):

    value = None

    def set(self, value):
        self.value = value

    def get(self, default=None):
        if self.value is None:
            return default
        return self.value