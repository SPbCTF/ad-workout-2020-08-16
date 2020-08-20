package notifier

import (
	"github.com/golang/protobuf/ptypes"
	"github.com/sirupsen/logrus"
	pb "gorepick/pb"
	"sync"
)

type Listener chan *pb.Event

type Notifier struct {
	log       *logrus.Entry
	listeners sync.Map
}

func New(log *logrus.Entry) *Notifier {
	return &Notifier{
		listeners: sync.Map{},
		log:       log,
	}
}

func (n *Notifier) Notify(e *pb.Event) {
	e.Timestamp = ptypes.TimestampNow()

	n.listeners.Range(func(key, value interface{}) bool {
		key.(Listener) <- e
		return true
	})
}

func (n *Notifier) Sub(listener Listener) {
	n.listeners.Store(listener, struct{}{})
}

func (n *Notifier) Unsub(listener Listener) {
	n.listeners.Delete(listener)
}
