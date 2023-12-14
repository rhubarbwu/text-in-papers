from typing import Any, Optional

from h5py import File


def commit(path: str, metric: str, new_val: Any, entry: Optional[str] = None):
    file = File(path, "a")
    if new_val is not None and entry is not None:
        if metric not in file:
            file.create_group(metric)
        if entry in file[metric]:
            del file[metric][entry]
        try:
            file[metric][entry] = new_val.cpu()
        except AttributeError:
            file[metric][entry] = new_val
    elif new_val is not None:
        if metric in file:
            del file[metric]
        file.create_dataset(metric, data=new_val.cpu())
    file.close()
