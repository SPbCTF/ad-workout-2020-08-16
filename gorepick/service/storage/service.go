package storage

import (
	"context"
	"fmt"
	"github.com/go-redis/redis/v8"
	"github.com/sirupsen/logrus"
	"gorepick/storage/notifier"
	"io/ioutil"
	"path/filepath"
	"strings"
)

const (
	scriptsDir        string = "storage/scripts"
	scriptsExt        string = ".lua"
	scriptsGlobFormat string = "%s/*%s"
)

type Service struct {
	rdb     *redis.Client
	scripts map[string]string
	notify  *notifier.Notifier
	log     *logrus.Entry
}

func New(redisAddr string, notify *notifier.Notifier, log *logrus.Entry) *Service {
	rdb := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	ctx := context.Background()
	status := rdb.Ping(ctx)
	if err := status.Err(); err != nil {
		logrus.WithError(err).Fatalf("can't ping redis!")
	}

	srv := &Service{
		rdb:    rdb,
		notify: notify,
		log:    log,
	}

	err := srv.load()
	if err != nil {
		logrus.WithError(err).Fatalf("can't load scripts")
	}

	return srv
}

func (s *Service) load() error {
	ctx := context.Background()
	s.scripts = make(map[string]string)

	cmd := s.rdb.ScriptFlush(ctx)
	if err := cmd.Err(); err != nil {
		return err
	}

	files, err := filepath.Glob(fmt.Sprintf(scriptsGlobFormat, scriptsDir, scriptsExt))
	if err != nil {
		return err
	}

	for _, file := range files {
		data, err := ioutil.ReadFile(file)
		if err != nil {
			return err
		}

		name := strings.TrimPrefix(strings.TrimSuffix(file, scriptsExt), scriptsDir)

		cmd := s.rdb.ScriptLoad(ctx, string(data))
		hash, err := cmd.Result()
		if err != nil {
			return err
		}

		s.log.Infof("Loaded script %s: %s", name, hash)
		s.scripts[name] = hash
	}

	return nil
}

func (s *Service) Sub(l notifier.Listener) {
	s.notify.Sub(l)
}

func (s *Service) Unsub(l notifier.Listener) {
	s.notify.Unsub(l)
}
