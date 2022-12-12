from .utils.bunch import Bunch

colors = Bunch(
    {
        "error": "#FF0000",
    }
)

modules = Bunch(
    {
        "models": Bunch(
            {"color": "#598c14"},
        ),
        "data_loaders": Bunch({"color": "#4a8594"}),
        "trainers": Bunch({"color": "yellow"}),
        "experiments": Bunch({"color": "#ff6908"}),
    }
)
