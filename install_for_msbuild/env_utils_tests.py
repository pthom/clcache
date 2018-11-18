#!/usr/bin/env python
import unittest
import env_utils
import locate_cl_exe

class EnvUtilsTests(unittest.TestCase):
    def testEnvVars(self):
        env_utils.setAndStoreEnvVariable("DUMMYVAR", "dummy")
        result = env_utils.readEnvVariableFromRegistry("DUMMYVAR")
        self.assertEqual(result, "dummy")
        env_utils.removeEnvVariable("DUMMYVAR")
        result = env_utils.readEnvVariableFromRegistry("DUMMYVAR")
        self.assertTrue(result is None)


class LocateClTests(unittest.TestCase):
    def testFindfindMsvcUpTo2015(self):
        result = locate_cl_exe.implFindMsvcUpTo2015()
        self.assertTrue(len(result) > 0)
    def testFindMsvc2017(self):
        aux = locate_cl_exe.implFindMsvc2017()
        self.assertTrue(len(aux) >= 0)
    def testFindMsvc(self):
        aux = locate_cl_exe.findMsvc()
        self.assertTrue(len(aux) > 0)
    def testFindCl(self):
        aux = locate_cl_exe.findClExesList()
        self.assertTrue(len(aux) > 0)


if __name__ == '__main__':
    unittest.TestCase.longMessage = True
    unittest.main()
