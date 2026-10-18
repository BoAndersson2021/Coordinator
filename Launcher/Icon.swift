import AppKit

// Draw a native icon; no external assets or image services are needed.
let output = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
for size in [16, 32, 128, 256, 512] {
    for scale in [1, 2] {
        let pixels = size * scale
        let image = NSImage(size: NSSize(width: 1024, height: 1024))
        image.lockFocus()
        let background = NSBezierPath(roundedRect: NSRect(x: 44, y: 44, width: 936, height: 936), xRadius: 210, yRadius: 210)
        NSGradient(starting: NSColor(calibratedRed: 0.08, green: 0.17, blue: 0.27, alpha: 1),
                   ending: NSColor(calibratedRed: 0.02, green: 0.06, blue: 0.11, alpha: 1))!.draw(in: background, angle: -75)
        NSColor(calibratedRed: 0.35, green: 0.93, blue: 0.77, alpha: 1).setStroke()
        let chevron = NSBezierPath()
        chevron.lineWidth = 53
        chevron.lineCapStyle = .round
        chevron.lineJoinStyle = .round
        chevron.move(to: NSPoint(x: 256, y: 675))
        chevron.line(to: NSPoint(x: 415, y: 530))
        chevron.line(to: NSPoint(x: 256, y: 385))
        chevron.stroke()
        let cursor = NSBezierPath()
        cursor.lineWidth = 45
        cursor.lineCapStyle = .round
        cursor.move(to: NSPoint(x: 501, y: 385))
        cursor.line(to: NSPoint(x: 736, y: 385))
        cursor.stroke()
        let label = "2" as NSString
        label.draw(at: NSPoint(x: 660, y: 588), withAttributes: [
            .font: NSFont.monospacedSystemFont(ofSize: 160, weight: .bold),
            .foregroundColor: NSColor.white
        ])
        image.unlockFocus()
        let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: pixels, pixelsHigh: pixels,
                                      bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true,
                                      isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
        image.draw(in: NSRect(x: 0, y: 0, width: pixels, height: pixels))
        NSGraphicsContext.restoreGraphicsState()
        let suffix = scale == 2 ? "@2x" : ""
        try bitmap.representation(using: .png, properties: [:])!.write(
            to: output.appendingPathComponent("icon_\(size)x\(size)\(suffix).png"))
    }
}
