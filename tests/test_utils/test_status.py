#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from unittest import TestCase

import mock

from sophon.utils.status import get_host_status


class TestGetHostStatus(TestCase):

    @mock.patch("sophon.utils.status.subprocess")
    def test_get_host_status_with_server_available(self, _subprocess):
        _subprocess.Popen.return_value.stdout.read.side_effect = [
            """
top - 23:42:26 up 31 days,  7:46,  1 user,  load average: 0.00, 0.01, 0.05
Tasks:  72 total,   1 running,  71 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.1 us,  0.1 sy,  0.0 ni, 99.7 id,  0.1 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem:   1024468 total,   936860 used,    87608 free,   119512 buffers
KiB Swap:  2097148 total,     1528 used,  2095620 free.   582932 cached Mem

PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND
  1 root      20   0   28288   3920   2624 S  0.0  0.4   0:17.44 systemd
  2 root      20   0       0      0      0 S  0.0  0.0   0:00.00 kthreadd
  3 root      20   0       0      0      0 S  0.0  0.0   0:09.92 ksoftirqd/0
  5 root       0 -20       0      0      0 S  0.0  0.0   0:00.00 kworker/0:0H
  6 root      20   0       0      0      0 S  0.0  0.0   0:11.30 kworker/u2:0
  7 root      20   0       0      0      0 S  0.0  0.0   0:19.66 rcu_sched
  8 root      20   0       0      0      0 S  0.0  0.0   0:00.00 rcu_bh
  9 root      rt   0       0      0      0 S  0.0  0.0   0:00.00 migration/0
            """,
            """
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1       7.8G  1.7G  5.8G  23% /
            """
        ]
        result = get_host_status("123.123.123.123")
        self.assertEqual(
            _subprocess.Popen.call_args_list,
            [
                mock.call("ansible 123.123.123.123 -a \"top -b -n 1\"",
                          shell=True, stdout=_subprocess.PIPE),
                mock.call("ansible 123.123.123.123 -a \"df -h .\"",
                          shell=True, stdout=_subprocess.PIPE),
            ]
        )
        self.assertEqual(
            _subprocess.Popen.return_value.stdout.read.call_count, 2
        )
        self.assertEqual(
            result,
            {
                "Status": "Active",
                "Memory Usage": (914, 1000),
                "CPU Load": 0.0,
                "Disk Usage": (1.7, 7.8)
            }
        )

    @mock.patch("sophon.utils.status.subprocess")
    def test_get_host_status_with_server_outage(self, _subprocess):
        _subprocess.Popen.return_value.stdout.read.side_effect = ["", ""]
        result = get_host_status("123.123.123.123")
        self.assertEqual(
            _subprocess.Popen.call_args_list,
            [
                mock.call("ansible 123.123.123.123 -a \"top -b -n 1\"",
                          shell=True, stdout=_subprocess.PIPE),
                mock.call("ansible 123.123.123.123 -a \"df -h .\"",
                          shell=True, stdout=_subprocess.PIPE),
            ]
        )
        self.assertEqual(
            _subprocess.Popen.return_value.stdout.read.call_count, 2
        )
        self.assertEqual(
            result,
            {
                "Status": "Down",
                "Memory Usage": (0, 0),
                "CPU Load": 0.0,
                "Disk Usage": (0.0, 0.0)
            }
        )
