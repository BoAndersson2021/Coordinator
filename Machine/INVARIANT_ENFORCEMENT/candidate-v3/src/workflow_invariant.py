"""Mandatory execution barrier. No current adapter has qualified automation.

This is an enforced stop, not an implementation of lifecycle/orchestration.
There is deliberately no configuration, environment or CLI override or allow
branch. Introducing one requires a separately reviewed runtime implementation.
"""

INVARIANT = 'MACHINE_AUTOMATED_EXECUTION_REQUIRED'
EXIT_CODE = 3

# Closed inventory: unknown adapters and new CLI operations cannot inherit access.
ADAPTERS = ('machine.coordinator', 'native.inspection', 'manual.inspection', 'scratch.init')
SOURCE_MODULES = ('machine.py', 'admission.py', 'native_bridge.py', 'native_socket.py',
                  'workflow_invariant.py')
RUNTIME_FILES = ('Machine', '.githooks/pre-commit', 'scripts/check_workflow_invariant.py',
                 *(('src/' + name) for name in SOURCE_MODULES))
MISSING = ('persistent_orchestration', 'managed_executor_lifecycle',
           'exact_live_receiver_binding', 'automatic_communication_and_handover',
           'observable_supervision_and_recovery')

ADMIN_COMMANDS = frozenset(('init', 'project-register', 'agent-bind', 'task-prepare',
                          'bridge-configure', 'bridge-observe', 'session-admit', 'permit-issue'))
EVIDENCE_COMMANDS = frozenset(('task-show', 'evidence-show', 'task-acknowledge',
                             'task-uncertain', 'task-reconcile', 'task-report'))
HEALTH_COMMANDS = frozenset(('status', 'doctor', 'work-view', 'bridge-collect',
                           'permit-inspect', 'invariant-check'))
WORKFLOW_COMMANDS = frozenset(('task-dispatch', 'bridge-send', 'permit-execute',
                             'task-replacement-begin', 'task-replacement-finish',
                             'task-verify', 'task-close'))


def assessment(adapter='machine.coordinator', operation='workflow'):
    return {'schema_version': 1, 'code': INVARIANT, 'severity': 'error',
            'status': 'workflow_invariant_failed', 'workflow_ready': False,
            'adapter': adapter, 'operation': operation,
            'reason': ('Adapter is unknown and unqualified' if adapter not in ADAPTERS else
                       'Current implementation requires manual lifecycle or orchestration'),
            'missing_capabilities': list(MISSING), 'manual_fallback_permitted': False,
            'adapters': [{'id': name, 'qualified': False} for name in ADAPTERS],
            'required_action': 'Implement and independently qualify automatic execution; '
                               'preserve unresolved work. Do not start a terminal or relay messages manually.'}


class InvariantViolation(ValueError):
    def __init__(self, adapter, operation):
        self.record = assessment(adapter, operation)
        super().__init__(INVARIANT + ': ' + self.record['reason'])


def require_automated_workflow(adapter, operation):
    # A declaration, permit, source PASS, idle/notLoaded thread or caller label
    # cannot turn missing runtime capabilities into a qualified executor.
    raise InvariantViolation(adapter, operation)


def command_kind(command):
    command = command or 'status'
    for kind, commands in (('admin', ADMIN_COMMANDS), ('evidence', EVIDENCE_COMMANDS),
                           ('health', HEALTH_COMMANDS), ('workflow', WORKFLOW_COMMANDS)):
        if command in commands:
            return kind
    require_automated_workflow('unknown', command)


def guard_command(command):
    kind = command_kind(command)
    if kind == 'workflow':
        require_automated_workflow('machine.coordinator', command)
    return kind


def runtime_files(root):
    """All executable code belongs to the closed inventory, including scripts."""
    code_extensions = {'.py', '.sh', '.command', '.js', '.mjs', '.ts', '.rs', '.go',
                       '.c', '.h', '.cc', '.cpp', '.so', '.dylib', '.wasm'}
    protected_trees = {'src', 'scripts', 'adapters', 'providers', 'tools', '.githooks'}
    found = set()
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if not path.is_file() or relative.parts[0] in ('.git', '.machine', 'Design', 'tests'):
            continue
        if '__pycache__' in relative.parts:
            continue
        if (relative.parts[0] in protected_trees or path.suffix in code_extensions
                or path.stat().st_mode & 0o111 or str(relative) == 'Machine'):
            found.add(str(relative))
    return found
