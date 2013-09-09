#!/usr/bin/env python
# Tests for the Task module

import unittest
import pomito.task

import sure

class TaskTests(unittest.TestCase):
    """TODO: incomplete"""
    def test_task_should_set_attributes(self):
        _task = pomito.task.Task(description="A Simple Task", estimate="20",
                actual=100, tags='sample tag', uid=111)
        _task.description.should.be.equal("A Simple Task")
        _task.estimate.should.be.equal(20)
        _task.actual.should.be.equal(100)
        _task.tags.should.be.equal('sample tag')
        _task.uid.should.be.equal(111)
