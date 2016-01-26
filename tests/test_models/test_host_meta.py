#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
from unittest import TestCase

import mock

from sophon.models import HostMeta
from tests.test_models.conftest import mysql_fixture


class TestHostMeta(TestCase):

    @mysql_fixture
    def test_insert(self, session):
        _insert_data = HostMeta(hostname="Marvin", ip="123.456.78.9")
        session.add(_insert_data)

        _query_data = session.query(HostMeta).filter_by(
            hostname="Marvin"
        ).first()
        self.assertEqual(_query_data.hostname, "Marvin")
        self.assertEqual(_query_data.ip, "123.456.78.9")
        self.assertEqual(_query_data.status, json.dumps(
            {
                "Hostname": "Marvin",
                "IP": "123.456.78.9",
                "Status": "Down",
                "CPU Load": 0,
                "Memory Usage": (0, 0),
                "Disk Usage": (0, 0)
            }
        ))

        self.assertEqual(_query_data.process_status, json.dumps([]))
        self.assertEqual(_query_data.supervisor_status, json.dumps([]))

    @mysql_fixture
    def test_get_all_hosts_status(self, session):
        _insert_data = HostMeta(hostname="Marvin", ip="123.456.78.9")
        session.add(_insert_data)

        with mock.patch.object(
            HostMeta, "query", session.query_property()
        ) as _query:
            hosts_status = HostMeta.get_all_hosts_status()
            self.assertEqual(hosts_status, {
                1: {
                    "Hostname": "Marvin",
                    "IP": "123.456.78.9",
                    "Status": "Down",
                    "CPU Load": 0,
                    "Memory Usage": [0, 0],
                    "Disk Usage": [0, 0]
                }
            })

    @mysql_fixture
    @mock.patch("sophon.models.host_meta.session")
    def test_update_host_status(self, session, _session):
        _commit = mock.Mock()
        _session.commit = _commit

        _insert_data = HostMeta(hostname="Marvin", ip="123.456.78.9")
        session.add(_insert_data)

        with mock.patch.object(
            HostMeta, "query", session.query_property()
        ) as _query:
            HostMeta.update_host_status(
                "123.456.78.9",
                {
                    "Hostname": "Marvin",
                    "IP": "123.456.78.9",
                    "Status": "Active",
                    "CPU Load": 0.1,
                    "Memory Usage": [2000, 5000],
                    "Disk Usage": [20, 40]
                }
            )
            _commit.called_once_with()
            _query_data = session.query(HostMeta).filter_by(
                hostname="Marvin"
            ).first()
            self.assertEqual(_query_data.status, json.dumps(
                {
                    "Hostname": "Marvin",
                    "IP": "123.456.78.9",
                    "Status": "Active",
                    "CPU Load": 0.1,
                    "Memory Usage": [2000, 5000],
                    "Disk Usage": [20, 40]
                }
            ))

    @mysql_fixture
    def test_get_host_process_status(self, session):
        _insert_data = HostMeta(hostname="Marvin", ip="123.456.78.9")
        _insert_data.process_status = json.dumps([
            {
                "PID": 1,
                "User": "root",
                "Memory Usage": 0.1,
                "CPU Usage": 0.2,
                "Time": "11:11:11",
                "Command": "/bin/place/holder"
            }
        ])
        session.add(_insert_data)

        with mock.patch.object(
            HostMeta, "query", session.query_property()
        ) as _query:
            _id = HostMeta.query.all()[-1].id
            hosts_process_status = HostMeta.get_host_process_status(
                host_id=_id
            )
            self.assertEqual(hosts_process_status, [
                {
                    "PID": 1,
                    "User": "root",
                    "Memory Usage": 0.1,
                    "CPU Usage": 0.2,
                    "Time": "11:11:11",
                    "Command": "/bin/place/holder"
                }
            ])

    @mysql_fixture
    @mock.patch("sophon.models.host_meta.session")
    def test_update_host_process_status(self, session, _session):
        _commit = mock.Mock()
        _session.commit = _commit

        _insert_data = HostMeta(hostname="Marvin", ip="123.456.78.9")
        session.add(_insert_data)

        with mock.patch.object(
            HostMeta, "query", session.query_property()
        ) as _query:
            HostMeta.update_host_process_status(
                "123.456.78.9",
                [{
                    "PID": 2,
                    "User": "toor",
                    "Memory Usage": 0.2,
                    "CPU Usage": 0.4,
                    "Time": "23:33:33",
                    "Command": "/bin/another/place/holder"
                }]
            )
            _commit.called_once_with()
            _query_data = session.query(HostMeta).filter_by(
                hostname="Marvin"
            ).first()
            self.assertEqual(_query_data.process_status, json.dumps(
                [{
                    "PID": 2,
                    "User": "toor",
                    "Memory Usage": 0.2,
                    "CPU Usage": 0.4,
                    "Time": "23:33:33",
                    "Command": "/bin/another/place/holder"
                }]
            ))