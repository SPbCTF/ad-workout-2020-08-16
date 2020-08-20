package api

import pb "gorepick/pb"

func (s *Server) Events(_ *pb.EventsRequest, conn pb.Api_EventsServer) error {

	events := make(chan *pb.Event)
	s.st.Sub(events)
	defer s.st.Unsub(events)

	for {
		select {
		case event := <-events:
			err := conn.Send(event)
			if err != nil {
				return err
			}
		case <-conn.Context().Done():
			return nil
		}
	}
}
