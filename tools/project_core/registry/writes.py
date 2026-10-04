"""Single-writer guard shared by all central workbook coordinators."""
import os
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def central_lock(root):
    lock=Path(root)/'.project-write.lock'
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise ValueError('Another central writer holds .project-write.lock; retry after it completes')
    try:
        os.write(fd,str(os.getpid()).encode());os.close(fd);yield
    finally:lock.unlink(missing_ok=True)
