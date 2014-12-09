from ..context import get_context

context_datastore_key = "datastreams"


def get_datastream(dsid):
    context = get_context()
    datastreams_data = context.get_data(context_datastore_key)
    if dsid not in datastreams_data:
        datastreams_data[dsid] = Datastream()
    return datastreams_data[dsid]


class Datastream(object):

    value = None

    def set(self, value):
        self.value = value

    def get(self):
        return self.value