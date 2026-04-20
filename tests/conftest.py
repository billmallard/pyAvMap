"""
Qt stubs for pyavmap testing — allows importing pyavmap without a display.
Installed before any test collection so all star-imports in pyavmap/__init__.py resolve.
"""
import sys
import types


def _make_qt_stub():
    """Return a module object with enough Qt names to let pyavmap/__init__.py import."""

    class _Dummy:
        def __init__(self, *a, **kw):
            pass
        def __call__(self, *a, **kw):
            return self
        def __getattr__(self, name):
            return self

    class _Qt:
        ScrollBarAlwaysOff = 0
        NoFocus = 0
        white = 0
        black = 0
        green = 0
        yellow = 0

    class QPointF(_Dummy):
        def __init__(self, x=0, y=0):
            self.x_val = x
            self.y_val = y
        def x(self): return self.x_val
        def y(self): return self.y_val

    class QGraphicsView(_Dummy): pass
    class QPainter(_Dummy):
        Antialiasing = 0
    class QColor(_Dummy): pass
    class QPolygonF(_Dummy): pass
    class QGraphicsScene(_Dummy): pass
    class QStyleOptionGraphicsItem(_Dummy): pass

    stub = types.ModuleType("_qt_stub")
    stub.Qt = _Qt
    stub.QPointF = QPointF
    stub.QGraphicsView = QGraphicsView
    stub.QPainter = QPainter
    stub.QColor = QColor
    stub.QPolygonF = QPolygonF
    stub.QGraphicsScene = QGraphicsScene
    stub.QStyleOptionGraphicsItem = QStyleOptionGraphicsItem
    return stub


_qt = _make_qt_stub()

for _mod_name in ("PyQt5", "PyQt5.QtGui", "PyQt5.QtCore", "PyQt5.QtWidgets",
                  "PyQt4", "PyQt4.QtGui", "PyQt4.QtCore"):
    if _mod_name not in sys.modules:
        sys.modules[_mod_name] = _qt

# Stub the avchart_proj sub-module
_proj = types.ModuleType("pyavmap.avchart_proj")
_proj.CT_SECTIONAL = 0
_proj.charts = {}
sys.modules.setdefault("pyavmap.avchart_proj", _proj)
