# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


class ScaLAPACKTest(rfm.RegressionTest):
    def __init__(self, linkage):
        self.linkage = linkage
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'scalapack')
        self.valid_systems = ['daint:gpu', 'daint:mc', 'dom:mc',
                              'dom:gpu', 'kesch:cn']
        self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
                                    'PrgEnv-intel']
        self.num_tasks = 16
        self.num_tasks_per_node = 8
        self.variables = {'CRAYPE_LINK_TYPE': linkage}
        if self.current_system.name == 'kesch':
            self.exclusive_access = True
            self.valid_prog_environs = ['PrgEnv-cray']
            if linkage == 'static':
                # Static linkage not supported on Kesch
                self.valid_prog_environs = []

        self.build_system = 'SingleSource'
        self.build_system.fflags = ['-O3']
        self.maintainers = ['CB', 'LM']
        self.tags = {'production', 'external-resources'}

    @rfm.run_before('compile')
    def cray_linker_workaround(self):
        # NOTE: Workaround for using CCE < 9.1 in CLE7.UP01.PS03 and above
        # See Patch Set README.txt for more details.
        if (self.current_system.name == 'dom' and
            self.current_environ.name == 'PrgEnv-cray'):
            self.variables['LINKER_X86_64'] = '/usr/bin/ld'


@rfm.required_version('>=2.14')
@rfm.parameterized_test(['static'], ['dynamic'])
class ScaLAPACKSanity(ScaLAPACKTest):
    def __init__(self, linkage):
        super().__init__(linkage)
        self.sourcepath = 'scalapack_compile_run.f'

        def fortran_float(value):
            return float(value.replace('D', 'E'))

        def scalapack_sanity(number1, number2, expected_value):
            symbol = 'z{0}{1}'.format(number1, number2)
            pattern = r'Z\(     {0},     {1}\)=\s+(?P<{2}>\S+)'.format(
                number2, number1, symbol)
            found_value = sn.extractsingle(pattern, self.stdout, symbol,
                                           fortran_float)
            return sn.assert_lt(sn.abs(expected_value - found_value), 1.0e-15)

        self.sanity_patterns = sn.all([
            scalapack_sanity(1, 1, -0.04853779318803846),
            scalapack_sanity(1, 2, -0.12222271866735863),
            scalapack_sanity(1, 3, -0.28248513530339736),
            scalapack_sanity(1, 4, 0.95021462733774853),
            scalapack_sanity(2, 1, 0.09120722270314352),
            scalapack_sanity(2, 2, 0.42662009209279039),
            scalapack_sanity(2, 3, -0.8770383032575241),
            scalapack_sanity(2, 4, -0.2011973015939371),
            scalapack_sanity(3, 1, 0.4951930430455262),
            scalapack_sanity(3, 2, -0.7986420412618930),
            scalapack_sanity(3, 3, -0.2988441319801194),
            scalapack_sanity(3, 4, -0.1662736444220721),
            scalapack_sanity(4, 1, 0.8626176298213052),
            scalapack_sanity(4, 2, 0.4064822185450869),
            scalapack_sanity(4, 3, 0.2483911184660867),
            scalapack_sanity(4, 4, 0.1701907253504270)
        ])
