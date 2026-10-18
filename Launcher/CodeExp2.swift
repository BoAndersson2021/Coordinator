import AppKit
import Darwin

enum LauncherError: LocalizedError {
    case invalid(String)
    var errorDescription: String? {
        switch self { case .invalid(let message): return message }
    }
}

enum Launcher {
    static let workspace = URL(fileURLWithPath: "/Users/boandersson/Desktop/CodeExp2", isDirectory: true)
    static let codex = "/Users/boandersson/.local/bin/codex"
    static let prompt = "onboard"
    static let fm = FileManager.default

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
        print("CodeExp2 — starting Coordinator onboarding…")
        fflush(stdout)
        // Hand the actual Terminal to Codex. No injected input, delays, permission
        // overrides, model overrides, session reuse, or synthetic readiness claims.
        var argv: [UnsafeMutablePointer<CChar>?] = []
        for argument in [codex, prompt] {
            argv.append(argument.withCString { strdup($0) })
        }
        argv.append(nil)
        defer { argv.forEach { free($0) } }
        argv.withUnsafeBufferPointer { _ = execv(codex, $0.baseAddress!) }
        throw LauncherError.invalid("Codex failed to start: \(String(cString: strerror(errno)))")
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
    switch Array(CommandLine.arguments.dropFirst()) {
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
    default: throw LauncherError.invalid("Supported options: --preflight, --terminal, --install-alias, --self-test")
    }
} catch {
    FileHandle.standardError.write(Data("CodeExp2: \(error.localizedDescription)\n".utf8))
    exit(1)
}
