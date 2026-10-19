import AppKit
import Darwin

enum LauncherError: LocalizedError {
    case invalid(String)
    var errorDescription: String? {
        switch self { case .invalid(let message): return message }
    }
}

// Permanent files, ephemeral kernel locks. Never unlink a claim file: doing so
// could let a second process lock a different inode under the same name.
final class InstanceClaim {
    static let names = ["Odin", "Thor", "Freya", "Loki", "Tyr", "Heimdall",
                        "Balder", "Frigg", "Njord", "Freyr", "Skadi", "Idunn"]
    static let colors: [UInt32] = [0x19334d, 0x4c211b, 0x482440, 0x18422c,
        0x483a16, 0x124346, 0x2e2853, 0x4d2630, 0x163f59, 0x35451e, 0x2c3f49, 0x40304c]
    static let capacity = names.count * 16
    let slot: Int
    let descriptor: Int32
    static func alias(for slot: Int) -> String { names[slot % 12] + (slot < 12 ? "" : "-\(slot / 12 + 1)") }
    static func color(for slot: Int) -> String { String(format: "#%06x", colors[slot % 12] + UInt32(slot / 12) * 0x020202) }
    var alias: String { Self.alias(for: slot) }
    var color: String { Self.color(for: slot) }

    init(slot: Int, descriptor: Int32) { self.slot = slot; self.descriptor = descriptor }
    deinit { close(descriptor) }

    static func acquire(in directory: URL) throws -> InstanceClaim {
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true,
                                                attributes: [.posixPermissions: 0o700])
        for slot in 0..<capacity {
            let path = directory.appendingPathComponent("\(slot).lock").path
            let fd = open(path, O_RDWR | O_CREAT | O_NOFOLLOW | O_CLOEXEC, 0o600)
            guard fd >= 0 else { throw LauncherError.invalid("Cannot open instance claim: \(String(cString: strerror(errno)))") }
            var info = stat()
            guard fstat(fd, &info) == 0, (info.st_mode & S_IFMT) == S_IFREG, info.st_uid == geteuid() else {
                close(fd)
                throw LauncherError.invalid("Instance claim is not an owned regular file: \(path)")
            }
            // Process-associated record locks survive exec, but not fork. A
            // helper inheriting this fd cannot retain the claim after TUI death.
            var record = flock()
            record.l_type = Int16(F_WRLCK)
            record.l_whence = Int16(SEEK_SET)
            if fcntl(fd, F_SETLK, &record) == 0 {
                // execv must carry this descriptor into the actual native Codex
                // process, not a JS wrapper that closes extra child descriptors.
                guard fcntl(fd, F_SETFD, 0) == 0 else {
                    close(fd)
                    throw LauncherError.invalid("Cannot retain instance claim across launch.")
                }
                return InstanceClaim(slot: slot, descriptor: fd)
            }
            let error = errno
            close(fd)
            guard error == EAGAIN || error == EACCES else {
                throw LauncherError.invalid("Cannot lock instance claim: \(String(cString: strerror(error)))")
            }
        }
        throw LauncherError.invalid("All \(capacity) CodeExp2 name/color pairs are occupied.")
    }
}

enum Launcher {
    static let workspace = URL(fileURLWithPath: "/Users/boandersson/Desktop/CodeExp2", isDirectory: true)
    // Same native executable used by the installed npm CLI. Direct exec keeps
    // the claim in the interactive process; no wrapper, supervisor or daemon.
    static let codex = "/Users/boandersson/.npm-global/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex"
    static let prompt = "onboard"
    static let fm = FileManager.default
    static let claimDirectory = workspace.appendingPathComponent("Launcher/build/instance-claims")

    static func initialPrompt(for claim: InstanceClaim) -> String {
        """
        onboard

        Launcher-assigned instance alias: \(claim.alias). Introduce yourself as Coordinator \(claim.alias).
        Your Terminal color is \(claim.color). This is a human alias for this running instance,
        not a replacement for your real session ID or role. Preserve actual IDs in structured messages.
        No mission is selected. Follow the normal onboarding checklist and present the mission menu.
        """
    }

    static func appearance(for claim: InstanceClaim) -> String {
        // OSC changes only this terminal, including its default background when
        // the TUI clears/redraws. It does not edit saved/default profiles.
        "\u{1b}]0;CodeExp2 — \(claim.alias)\u{07}\u{1b}]10;#f4f4f4\u{07}\u{1b}]11;\(claim.color)\u{07}\u{1b}]12;#ffffff\u{07}"
    }

    static func launchArguments(for claim: InstanceClaim) -> [String] {
        // An empty display-item list prevents the TUI replacing our alias title.
        // This is the only config override; permissions/model/account are inherited.
        [codex, "--config", "tui.terminal_title=[]", initialPrompt(for: claim)]
    }

    static func validate(workspace root: URL = workspace, executable: String = codex) throws {
        var directory: ObjCBool = false
        guard fm.fileExists(atPath: root.path, isDirectory: &directory), directory.boolValue,
              root.resolvingSymlinksInPath().path == root.standardizedFileURL.path else {
            throw LauncherError.invalid("Workspace is missing or redirected: \(root.path)")
        }
        for name in ["AGENTS.md", "README.md", "Mission_Sofar.md", "Missions/README.md"] {
            guard fm.isReadableFile(atPath: root.appendingPathComponent(name).path) else {
                throw LauncherError.invalid("Required workspace document is missing or unreadable: \(name)")
            }
        }
        guard fm.isExecutableFile(atPath: executable) else {
            throw LauncherError.invalid("Codex is missing or not executable: \(executable)")
        }
    }

    static func preflight() throws {
        try validate()
        // Filesystem-only check: never start Codex or a model task here.
        print("PASS: CodeExp2 workspace and Codex executable are available.")
        print("Workspace: \(workspace.path)\nCommand: \(codex) \(prompt)")
    }

    static func runInTerminal() throws -> Never {
        try validate()
        guard isatty(STDIN_FILENO) == 1, isatty(STDOUT_FILENO) == 1 else {
            throw LauncherError.invalid("Open CodeExp2.app to start an interactive Terminal session.")
        }
        guard chdir(workspace.path) == 0 else {
            throw LauncherError.invalid("Cannot enter workspace: \(String(cString: strerror(errno)))")
        }
        let claim = try InstanceClaim.acquire(in: claimDirectory)
        print(appearance(for: claim), terminator: "")
        print("CodeExp2 — Coordinator \(claim.alias) — \(claim.color)")
        print("Starting Coordinator onboarding…")
        fflush(stdout)
        // Hand the actual Terminal to Codex. No injected input, delays, permission
        // overrides, model overrides, session reuse, or synthetic readiness claims.
        var argv: [UnsafeMutablePointer<CChar>?] = []
        for argument in launchArguments(for: claim) {
            argv.append(argument.withCString { strdup($0) })
        }
        argv.append(nil)
        defer { argv.forEach { free($0) } }
        withExtendedLifetime(claim) {
            argv.withUnsafeBufferPointer { _ = execv(codex, $0.baseAddress!) }
        }
        throw LauncherError.invalid("Codex failed to start: \(String(cString: strerror(errno)))")
    }

    // Disposable process-level regression entry: no Terminal or Codex launch.
    // EOF/termination releases the claim exactly as a terminated session does.
    static func claimProbe(_ root: String, withChild: Bool = false) throws {
        let claim = try InstanceClaim.acquire(in: URL(fileURLWithPath: root))
        let arguments = [CommandLine.arguments[0], "--inherited-claim-probe",
                         String(claim.slot), String(claim.descriptor), withChild ? "child" : "alone"]
        let argv = arguments.map { strdup($0) } + [nil]
        defer { argv.forEach { free($0) } }
        withExtendedLifetime(claim) {
            argv.withUnsafeBufferPointer { _ = execv(arguments[0], $0.baseAddress!) }
        }
        throw LauncherError.invalid("Claim regression exec failed.")
    }

    static func inheritedClaimProbe(slot: Int, descriptor: Int32, withChild: Bool) throws {
        guard (0..<InstanceClaim.capacity).contains(slot), descriptor > 2,
              fcntl(descriptor, F_GETFD) >= 0 else { throw LauncherError.invalid("Claim did not survive exec.") }
        let claim = InstanceClaim(slot: slot, descriptor: descriptor)
        var child: pid_t = 0
        if withChild {
            // Deliberately outlive the owner while retaining the claim fd.
            // No CLOEXEC_DEFAULT spawn flag: the regression verifies this fd
            // in the child and explicitly terminates its bounded sleep process.
            var argv = [strdup("/bin/sleep"), strdup("60"), nil]
            defer { argv.forEach { free($0) } }
            let result = argv.withUnsafeMutableBufferPointer {
                posix_spawn(&child, "/bin/sleep", nil, nil, $0.baseAddress!, nil)
            }
            guard result == 0 else { throw LauncherError.invalid("Cannot spawn descriptor-inheritance fixture.") }
        }
        let data = try JSONSerialization.data(withJSONObject: ["alias": claim.alias, "color": claim.color,
                    "slot": slot, "pid": getpid(), "fd": descriptor,
                    "child_pid": child,
                    "appearance": appearance(for: claim), "arguments": launchArguments(for: claim)])
        FileHandle.standardOutput.write(data + Data([10]))
        withExtendedLifetime(claim) { _ = FileHandle.standardInput.readDataToEndOfFile() }
    }

    static func installAlias() throws {
        let bundle = Bundle.main.bundleURL
        guard bundle.pathExtension == "app", bundle.lastPathComponent == "CodeExp2.app" else {
            throw LauncherError.invalid("Run --install-alias from the built CodeExp2.app executable.")
        }
        let alias = workspace.deletingLastPathComponent().appendingPathComponent("CodeExp2.app")
        // Preserve any existing Desktop object, including an unrelated alias.
        guard !fm.fileExists(atPath: alias.path), (try? alias.resourceValues(forKeys: [.isAliasFileKey])) == nil else {
            throw LauncherError.invalid("Desktop item already exists; left unchanged: \(alias.path)")
        }
        let bookmark = try bundle.bookmarkData(options: .suitableForBookmarkFile,
                                               includingResourceValuesForKeys: nil, relativeTo: nil)
        try URL.writeBookmarkData(bookmark, to: alias)
        let icon = NSWorkspace.shared.icon(forFile: bundle.path)
        guard NSWorkspace.shared.setIcon(icon, forFile: alias.path, options: []) else {
            throw LauncherError.invalid("Alias was created, but its icon could not be applied: \(alias.path)")
        }
        print("Created native Finder alias: \(alias.path)\nOriginal: \(bundle.path)")
    }

    static func selfTest() throws {
        let scratch = fm.temporaryDirectory.appendingPathComponent("codeexp2-launcher-\(UUID().uuidString)")
        try fm.createDirectory(at: scratch.appendingPathComponent("Missions"), withIntermediateDirectories: true)
        defer { try? fm.removeItem(at: scratch) }
        let root = scratch.resolvingSymlinksInPath()
        let executable = root.appendingPathComponent("fake-codex")
        try Data("#!/bin/sh\nexit 99\n".utf8).write(to: executable)
        try fm.setAttributes([.posixPermissions: 0o755], ofItemAtPath: executable.path)
        for name in ["AGENTS.md", "README.md", "Mission_Sofar.md", "Missions/README.md"] {
            try Data("fixture\n".utf8).write(to: root.appendingPathComponent(name))
        }
        try validate(workspace: root, executable: executable.path)
        func mustReject(_ name: String, _ action: () throws -> Void) throws {
            do { try action() } catch is LauncherError { print("PASS: \(name)"); return }
            throw LauncherError.invalid("Test failed: \(name)")
        }
        try mustReject("missing workspace") { try validate(workspace: root.appendingPathComponent("absent"), executable: executable.path) }
        try fm.removeItem(at: root.appendingPathComponent("AGENTS.md"))
        try mustReject("missing onboarding instructions") { try validate(workspace: root, executable: executable.path) }
        try Data("fixture\n".utf8).write(to: root.appendingPathComponent("AGENTS.md"))
        try fm.setAttributes([.posixPermissions: 0o644], ofItemAtPath: executable.path)
        try mustReject("non-executable Codex") { try validate(workspace: root, executable: executable.path) }
        let link = root.appendingPathComponent("redirected")
        try fm.createSymbolicLink(at: link, withDestinationURL: root)
        try mustReject("redirected workspace") { try validate(workspace: link, executable: codex) }
        let slots = 0..<InstanceClaim.capacity
        guard Set(slots.map { InstanceClaim.alias(for: $0) }).count == slots.count,
              Set(slots.map { InstanceClaim.color(for: $0) }).count == slots.count,
              InstanceClaim.alias(for: 12) == "Odin-2" else { throw LauncherError.invalid("Duplicate name/color pair.") }
        print("PASS: 192 distinct name/color pairs.")
        print("PASS: launcher preflight regressions; no Codex process launched.")
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        do {
            try Launcher.validate()
            guard let script = Bundle.main.url(forResource: "Start CodeExp2", withExtension: "command"),
                  let terminal = NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.apple.Terminal") else {
                throw LauncherError.invalid("Terminal or the bundled launch command is missing.")
            }
            let configuration = NSWorkspace.OpenConfiguration()
            configuration.activates = true
            NSWorkspace.shared.open([script], withApplicationAt: terminal, configuration: configuration) { _, error in
                DispatchQueue.main.async {
                    if let error { self.showError(error) }
                    NSApp.terminate(nil)
                }
            }
        } catch {
            showError(error)
            NSApp.terminate(nil)
        }
    }

    func showError(_ error: Error) {
        NSApp.setActivationPolicy(.regular)
        NSApp.activate(ignoringOtherApps: true)
        let alert = NSAlert()
        alert.messageText = "CodeExp2 could not start"
        alert.informativeText = error.localizedDescription
        alert.alertStyle = .critical
        alert.runModal()
    }
}

do {
    let arguments = Array(CommandLine.arguments.dropFirst())
    switch arguments {
    case []:
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.setActivationPolicy(.accessory)
        withExtendedLifetime(delegate) { app.run() }
    case ["--preflight"]: try Launcher.preflight()
    case ["--terminal"]: try Launcher.runInTerminal()
    case ["--install-alias"]: try Launcher.installAlias()
    case ["--self-test"]: try Launcher.selfTest()
    case let args where args.count == 2 && args[0] == "--claim-probe": try Launcher.claimProbe(args[1])
    case let args where args.count == 2 && args[0] == "--claim-probe-with-child": try Launcher.claimProbe(args[1], withChild: true)
    case let args where args.count == 4 && args[0] == "--inherited-claim-probe":
        guard let index = Int(args[1]), let fd = Int32(args[2]) else { throw LauncherError.invalid("Invalid claim probe.") }
        try Launcher.inheritedClaimProbe(slot: index, descriptor: fd, withChild: args[3] == "child")
    default: throw LauncherError.invalid("Supported options: --preflight, --terminal, --install-alias, --self-test")
    }
} catch {
    FileHandle.standardError.write(Data("CodeExp2: \(error.localizedDescription)\n".utf8))
    exit(1)
}
