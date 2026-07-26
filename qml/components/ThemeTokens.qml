pragma Singleton
import QtQuick

QtObject {
    // Brand colors
    readonly property color primary: "#6366F1" // Indigo 500
    readonly property color primaryDark: "#818CF8" // Indigo 400 (dark-mode primary)
    readonly property color accent: "#F59E0B" // Amber 400
    readonly property color accentDark: "#FCD34D" // Amber 300 (dark-mode accent)

    // Surface / card colors
    readonly property color surfaceLight: "#F8FAFC" // Slate 50
    readonly property color surfaceDark: "#0F172A" // Slate 900
    readonly property color cardLight: "#FFFFFF"
    readonly property color cardDark: "#1E293B" // Slate 800

    // Semantic colors
    readonly property color incomeGreen: "#10B981" // Emerald 500
    readonly property color expenseRed: "#EF4444" // Red 500
    readonly property color deficitAmberBg: "#FEF3C7" // Amber 100 (light)
    readonly property color deficitAmberBgDark: "#78350F" // Amber 900 (dark)
    readonly property color chartPositive: "#6366F1" // same as primary
    readonly property color chartNegTop: "#80EF4444" // semi-transparent red (deficit area)
    readonly property color chartNegBot: "#C0C62828"

    // Spacing scale (px)
    readonly property int spaceXs: 4
    readonly property int spaceSm: 8
    readonly property int spaceMd: 16
    readonly property int spaceLg: 24
    readonly property int spaceXl: 32

    // Border radii
    readonly property int radiusSm: 6
    readonly property int radiusMd: 10
    readonly property int radiusLg: 16
    readonly property int radiusFull: 9999

    // Font sizes
    readonly property int fontXs: 11
    readonly property int fontSm: 13
    readonly property int fontMd: 15
    readonly property int fontLg: 18
    readonly property int fontXl: 24
    readonly property int fontXxl: 32

    // Font weights (Qt uses integer weights)
    readonly property int weightRegular: Font.Normal // 400
    readonly property int weightMedium: Font.Medium // 500
    readonly property int weightSemiBold: Font.DemiBold // 600
    readonly property int weightBold: Font.Bold // 700

    // Monospace — generic "monospace" is not a real family on macOS; pick per platform.
    readonly property string fontMono: {
        switch (Qt.platform.os) {
        case "osx":
            return "Menlo";
        case "windows":
            return "Consolas";
        default:
            return "DejaVu Sans Mono";
        }
    }
}
