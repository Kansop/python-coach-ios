#!/usr/bin/env python3
"""Write PythonCoach.xcodeproj without XcodeGen or a Mac."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "PythonCoach.xcodeproj"
APP = "PythonCoach"
TESTS = "PythonCoachTests"


def uid(*parts: str) -> str:
    digest = hashlib.sha1("::".join(parts).encode()).hexdigest().upper()
    return digest[:24]


def pbx_quote(value: str) -> str:
    if value == "" or any(ch in value for ch in " \t;,$()"):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


class Project:
    def __init__(self) -> None:
        self.objects: dict[str, tuple[str, list[str]]] = {}

    def add(self, isa: str, key: str, body: list[str]) -> str:
        object_id = uid(isa, key)
        self.objects[object_id] = (isa, body)
        return object_id

    def render(self) -> str:
        sections: dict[str, list[tuple[str, list[str]]]] = {}
        for object_id, (isa, body) in self.objects.items():
            sections.setdefault(isa, []).append((object_id, body))
        chunks = ["// !$*UTF8*$!", "{", "\tarchiveVersion = 1;", "\tclasses = {", "\t};", "\tobjectVersion = 56;", "\tobjects = {"]
        for isa in sorted(sections):
            chunks.append(f"\n/* Begin {isa} section */")
            for object_id, body in sorted(sections[isa]):
                chunks.append(f"\t\t{object_id} /* {isa} */ = {{")
                chunks.append(f"\t\t\tisa = {isa};")
                chunks.extend(body)
                chunks.append("\t\t};")
            chunks.append(f"/* End {isa} section */")
        chunks.append("\t};")
        chunks.append(f"\trootObject = {uid('PBXProject', 'PythonCoach')};")
        chunks.append("}")
        chunks.append("")
        return "\n".join(chunks)


def file_type(path: Path) -> str:
    if path.suffix == ".swift":
        return "sourcecode.swift"
    if path.suffix == ".plist":
        return "text.plist.xml"
    if path.suffix == ".wav":
        return "audio.wav"
    if path.name.endswith(".xcassets"):
        return "folder.assetcatalog"
    return "text"


def main() -> None:
    project = Project()
    app_sources: list[str] = []
    app_resources: list[str] = []
    test_sources: list[str] = []

    def add_file(path: Path, group_key: str, role: str) -> str:
        ref = project.add(
            "PBXFileReference",
            str(path.relative_to(ROOT)),
            [
                f"\t\t\tlastKnownFileType = {file_type(path)};",
                f"\t\t\tpath = {pbx_quote(path.name)};",
                '\t\t\tsourceTree = "<group>";',
            ],
        )
        if role == "source":
            build = project.add(
                "PBXBuildFile",
                "source " + str(path.relative_to(ROOT)),
                [f"\t\t\tfileRef = {ref};"],
            )
            target_sources = test_sources if group_key == TESTS or group_key.startswith(TESTS + "/") else app_sources
            target_sources.append(build)
        elif role == "resource":
            build = project.add(
                "PBXBuildFile",
                "resource " + str(path.relative_to(ROOT)),
                [f"\t\t\tfileRef = {ref};"],
            )
            app_resources.append(build)
        return ref

    def add_group(directory: Path, key: str) -> str:
        children: list[str] = []
        for entry in sorted(directory.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
            if entry.name.startswith("."):
                continue
            if entry.is_dir() and entry.suffix != ".xcassets":
                children.append(add_group(entry, str(entry.relative_to(ROOT))))
                continue
            if entry.name == "Info.plist":
                children.append(add_file(entry, key, "plist"))
            elif entry.suffix == ".swift":
                children.append(add_file(entry, key, "source"))
            elif entry.suffix == ".xcassets" or entry.suffix == ".wav":
                children.append(add_file(entry, key, "resource"))
            else:
                children.append(add_file(entry, key, "resource"))
        child_list = ",\n".join(f"\t\t\t\t{child}" for child in children)
        return project.add(
            "PBXGroup",
            key,
            [
                "\t\t\tchildren = (",
                child_list,
                "\t\t\t);",
                f"\t\t\tpath = {pbx_quote(directory.name)};",
                '\t\t\tsourceTree = "<group>";',
            ],
        )

    app_group = add_group(ROOT / APP, APP)
    test_group = add_group(ROOT / TESTS, TESTS)

    app_product = project.add(
        "PBXFileReference",
        "product app",
        [
            '\t\t\texplicitFileType = wrapper.application;',
            '\t\t\tincludeInIndex = 0;',
            f"\t\t\tpath = {APP}.app;",
            '\t\t\tsourceTree = BUILT_PRODUCTS_DIR;',
        ],
    )
    test_product = project.add(
        "PBXFileReference",
        "product tests",
        [
            '\t\t\texplicitFileType = wrapper.cfbundle;',
            '\t\t\tincludeInIndex = 0;',
            f"\t\t\tpath = {TESTS}.xctest;",
            '\t\t\tsourceTree = BUILT_PRODUCTS_DIR;',
        ],
    )
    frameworks = []
    for name in ("SwiftUI", "WebKit", "AVFoundation", "SwiftData"):
        ref = project.add(
            "PBXFileReference",
            f"framework {name}",
            [
                "\t\t\tlastKnownFileType = wrapper.framework;",
                f"\t\t\tname = {name}.framework;",
                f"\t\t\tpath = System/Library/Frameworks/{name}.framework;",
                "\t\t\tsourceTree = SDKROOT;",
            ],
        )
        frameworks.append(
            project.add(
                "PBXBuildFile",
                f"link {name}",
                [f"\t\t\tfileRef = {ref};"],
            )
        )
    xctest = project.add(
        "PBXFileReference",
        "framework XCTest",
        [
            "\t\t\tlastKnownFileType = wrapper.framework;",
            "\t\t\tname = XCTest.framework;",
            "\t\t\tpath = System/Library/Frameworks/XCTest.framework;",
            "\t\t\tsourceTree = SDKROOT;",
        ],
    )
    xctest_build = project.add(
        "PBXBuildFile",
        "link XCTest",
        [f"\t\t\tfileRef = {xctest};"],
    )

    products = project.add(
        "PBXGroup",
        "Products",
        [
            "\t\t\tchildren = (",
            f"\t\t\t\t{app_product},",
            f"\t\t\t\t{test_product},",
            "\t\t\t);",
            "\t\t\tname = Products;",
            '\t\t\tsourceTree = "<group>";',
        ],
    )
    main_group = project.add(
        "PBXGroup",
        "main",
        [
            "\t\t\tchildren = (",
            f"\t\t\t\t{app_group},",
            f"\t\t\t\t{test_group},",
            f"\t\t\t\t{products},",
            "\t\t\t);",
            '\t\t\tsourceTree = "<group>";',
        ],
    )

    def phase(isa: str, key: str, files: list[str]) -> str:
        listing = ",\n".join(f"\t\t\t\t{item}" for item in files)
        return project.add(
            isa,
            key,
            [
                "\t\t\tbuildActionMask = 2147483647;",
                "\t\t\tfiles = (",
                listing,
                "\t\t\t);",
                "\t\t\trunOnlyForDeploymentPostprocessing = 0;",
            ],
        )

    app_sources_phase = phase("PBXSourcesBuildPhase", "app sources", app_sources)
    app_resources_phase = phase("PBXResourcesBuildPhase", "app resources", app_resources)
    app_frameworks_phase = phase("PBXFrameworksBuildPhase", "app frameworks", frameworks)
    test_sources_phase = phase("PBXSourcesBuildPhase", "test sources", test_sources)
    test_frameworks_phase = phase("PBXFrameworksBuildPhase", "test frameworks", [xctest_build])

    project_debug = project.add("XCBuildConfiguration", "project debug", settings_block(project_settings(debug=True)))
    project_release = project.add("XCBuildConfiguration", "project release", settings_block(project_settings(debug=False)))
    project_list = config_list(project, "project list", [project_debug, project_release])

    app_debug = project.add("XCBuildConfiguration", "app debug", settings_block(app_settings(debug=True)))
    app_release = project.add("XCBuildConfiguration", "app release", settings_block(app_settings(debug=False)))
    app_list = config_list(project, "app list", [app_debug, app_release])

    test_debug = project.add("XCBuildConfiguration", "test debug", settings_block(test_settings(debug=True)))
    test_release = project.add("XCBuildConfiguration", "test release", settings_block(test_settings(debug=False)))
    test_list = config_list(project, "test list", [test_debug, test_release])

    app_target = uid("PBXNativeTarget", APP)
    test_target = uid("PBXNativeTarget", TESTS)
    proxy = project.add(
        "PBXContainerItemProxy",
        "test proxy",
        [
            "\t\t\tcontainerPortal = " + uid("PBXProject", "PythonCoach") + ";",
            "\t\t\tproxyType = 1;",
            f"\t\t\tremoteGlobalIDString = {app_target};",
            f"\t\t\tremoteInfo = {APP};",
        ],
    )
    dependency = project.add(
        "PBXTargetDependency",
        "test depends app",
        [
            f"\t\t\ttarget = {app_target};",
            f"\t\t\ttargetProxy = {proxy};",
        ],
    )

    project.objects[app_target] = (
        "PBXNativeTarget",
        [
            "\t\t\tbuildConfigurationList = " + app_list + ";",
            "\t\t\tbuildPhases = (",
            f"\t\t\t\t{app_sources_phase},",
            f"\t\t\t\t{app_frameworks_phase},",
            f"\t\t\t\t{app_resources_phase},",
            "\t\t\t);",
            "\t\t\tbuildRules = (",
            "\t\t\t);",
            "\t\t\tdependencies = (",
            "\t\t\t);",
            f"\t\t\tname = {APP};",
            f"\t\t\tproductName = {APP};",
            f"\t\t\tproductReference = {app_product};",
            '\t\t\tproductType = "com.apple.product-type.application";',
        ],
    )
    project.objects[test_target] = (
        "PBXNativeTarget",
        [
            "\t\t\tbuildConfigurationList = " + test_list + ";",
            "\t\t\tbuildPhases = (",
            f"\t\t\t\t{test_sources_phase},",
            f"\t\t\t\t{test_frameworks_phase},",
            "\t\t\t);",
            "\t\t\tbuildRules = (",
            "\t\t\t);",
            "\t\t\tdependencies = (",
            f"\t\t\t\t{dependency},",
            "\t\t\t);",
            f"\t\t\tname = {TESTS};",
            f"\t\t\tproductName = {TESTS};",
            f"\t\t\tproductReference = {test_product};",
            '\t\t\tproductType = "com.apple.product-type.bundle.unit-test";',
        ],
    )

    project.add(
        "PBXProject",
        "PythonCoach",
        [
            "\t\t\tattributes = {",
            "\t\t\t\tBuildIndependentTargetsInParallel = 1;",
            "\t\t\t\tLastSwiftUpdateCheck = 1540;",
            "\t\t\t\tLastUpgradeCheck = 1540;",
            "\t\t\t\tTargetAttributes = {",
            f"\t\t\t\t\t{app_target} = {{",
            "\t\t\t\t\t\tCreatedOnToolsVersion = 15.4;",
            "\t\t\t\t\t};",
            f"\t\t\t\t\t{test_target} = {{",
            "\t\t\t\t\t\tCreatedOnToolsVersion = 15.4;",
            f"\t\t\t\t\t\tTestTargetID = {app_target};",
            "\t\t\t\t\t};",
            "\t\t\t\t};",
            "\t\t\t};",
            "\t\t\tbuildConfigurationList = " + project_list + ";",
            '\t\t\tcompatibilityVersion = "Xcode 14.0";',
            "\t\t\tdevelopmentRegion = en;",
            "\t\t\thasScannedForEncodings = 0;",
            "\t\t\tknownRegions = (",
            "\t\t\t\ten,",
            "\t\t\t\tBase,",
            "\t\t\t);",
            f"\t\t\tmainGroup = {main_group};",
            f"\t\t\tproductRefGroup = {products};",
            '\t\t\tprojectDirPath = "";',
            '\t\t\tprojectRoot = "";',
            "\t\t\ttargets = (",
            f"\t\t\t\t{app_target},",
            f"\t\t\t\t{test_target},",
            "\t\t\t);",
        ],
    )

    PROJECT.mkdir(parents=True, exist_ok=True)
    (PROJECT / "project.pbxproj").write_text(project.render(), encoding="utf-8")
    scheme_dir = PROJECT / "xcshareddata" / "xcschemes"
    scheme_dir.mkdir(parents=True, exist_ok=True)
    (scheme_dir / "PythonCoach.xcscheme").write_text(scheme(app_target, test_target), encoding="utf-8")
    print(f"sources={len(app_sources)} resources={len(app_resources)} tests={len(test_sources)}")


def settings_block(pairs: list[tuple[str, str]]) -> list[str]:
    name = "Debug"
    lines = ["\t\t\tbuildSettings = {"]
    for key, value in pairs:
        if key == "CONFIG_NAME":
            name = value
            continue
        lines.append(f"\t\t\t\t{key} = {value};")
    lines.append("\t\t\t};")
    lines.append(f"\t\t\tname = {name};")
    return lines


def config_list(project: Project, key: str, configs: list[str]) -> str:
    # The name (Debug/Release) is stored on the configuration, so rewrite the placeholder.
    listing = ",\n".join(f"\t\t\t\t{item}" for item in configs)
    return project.add(
        "XCConfigurationList",
        key,
        [
            "\t\t\tbuildConfigurations = (",
            listing,
            "\t\t\t);",
            "\t\t\tdefaultConfigurationIsVisible = 0;",
            "\t\t\tdefaultConfigurationName = Release;",
        ],
    )


def project_settings(debug: bool) -> list[tuple[str, str]]:
    rows = [
        ("ALWAYS_SEARCH_USER_PATHS", "NO"),
        ("CLANG_ANALYZER_NONNULL", "YES"),
        ("CLANG_ENABLE_MODULES", "YES"),
        ("CLANG_ENABLE_OBJC_ARC", "YES"),
        ("COPY_PHASE_STRIP", "NO"),
        ("DEBUG_INFORMATION_FORMAT", "dwarf" if debug else '"dwarf-with-dsym"'),
        ("ENABLE_STRICT_OBJC_MSGSEND", "YES"),
        ("ENABLE_USER_SCRIPT_SANDBOXING", "YES"),
        ("GCC_C_LANGUAGE_STANDARD", "gnu17"),
        ("IPHONEOS_DEPLOYMENT_TARGET", "17.0"),
        ("MTL_ENABLE_DEBUG_INFO", "INCLUDE_SOURCE" if debug else "NO"),
        ("ONLY_ACTIVE_ARCH", "YES" if debug else "NO"),
        ("SDKROOT", "iphoneos"),
        ("SWIFT_COMPILATION_MODE", "singlefile" if debug else "wholemodule"),
        ("SWIFT_OPTIMIZATION_LEVEL", '"-Onone"' if debug else '"-O"'),
        ("SWIFT_VERSION", "5.0"),
        ("CONFIG_NAME", "Debug" if debug else "Release"),
    ]
    if debug:
        rows.append(("SWIFT_ACTIVE_COMPILATION_CONDITIONS", "DEBUG"))
        rows.append(("ENABLE_TESTABILITY", "YES"))
    return rows


def app_settings(debug: bool) -> list[tuple[str, str]]:
    rows = [
        ("ASSETCATALOG_COMPILER_APPICON_NAME", "AppIcon"),
        ("ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME", "AccentColor"),
        ("CODE_SIGN_STYLE", "Automatic"),
        ("CURRENT_PROJECT_VERSION", "1"),
        ("ENABLE_PREVIEWS", "YES"),
        ("GENERATE_INFOPLIST_FILE", "NO"),
        ("INFOPLIST_FILE", "PythonCoach/Info.plist"),
        ("LD_RUNPATH_SEARCH_PATHS", '("$(inherited)", "@executable_path/Frameworks")'),
        ("MARKETING_VERSION", "1.0"),
        ("PRODUCT_BUNDLE_IDENTIFIER", "com.pythoncoach.app"),
        ("PRODUCT_NAME", '"$(TARGET_NAME)"'),
        ("SUPPORTED_PLATFORMS", '"iphoneos iphonesimulator"'),
        ("SUPPORTS_MACCATALYST", "NO"),
        ("SWIFT_EMIT_LOC_STRINGS", "YES"),
        ("SWIFT_STRICT_CONCURRENCY", "minimal"),
        ("SWIFT_VERSION", "5.0"),
        ("TARGETED_DEVICE_FAMILY", "\"1,2\""),
        ("CONFIG_NAME", "Debug" if debug else "Release"),
    ]
    if debug:
        rows.append(("ENABLE_TESTABILITY", "YES"))
    return rows


def test_settings(debug: bool) -> list[tuple[str, str]]:
    return [
        ("BUNDLE_LOADER", '"$(TEST_HOST)"'),
        ("CODE_SIGN_STYLE", "Automatic"),
        ("CURRENT_PROJECT_VERSION", "1"),
        ("GENERATE_INFOPLIST_FILE", "YES"),
        ("IPHONEOS_DEPLOYMENT_TARGET", "17.0"),
        ("LD_RUNPATH_SEARCH_PATHS", '("$(inherited)", "@executable_path/Frameworks", "@loader_path/Frameworks")'),
        ("MARKETING_VERSION", "1.0"),
        ("PRODUCT_BUNDLE_IDENTIFIER", "com.pythoncoach.app.tests"),
        ("PRODUCT_NAME", '"$(TARGET_NAME)"'),
        ("SDKROOT", "iphoneos"),
        ("SWIFT_EMIT_LOC_STRINGS", "NO"),
        ("SWIFT_STRICT_CONCURRENCY", "minimal"),
        ("SWIFT_VERSION", "5.0"),
        ("TARGETED_DEVICE_FAMILY", "\"1,2\""),
        ("TEST_HOST", '"$(BUILT_PRODUCTS_DIR)/PythonCoach.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/PythonCoach"'),
        ("CONFIG_NAME", "Debug" if debug else "Release"),
    ]


def scheme(app_target: str, test_target: str) -> str:
    def ref(target: str, name: str, kind: str) -> str:
        return f"""
         <BuildableReference
            BuildableIdentifier="primary"
            BlueprintIdentifier="{target}"
            BuildableName="{name}"
            BlueprintName="{name.split('.')[0]}"
            ReferencedContainer="container:PythonCoach.xcodeproj">
         </BuildableReference>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion="1540"
   version="1.7">
   <BuildAction
      parallelizeBuildables="YES"
      buildImplicitDependencies="YES">
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting="YES"
            buildForRunning="YES"
            buildForProfiling="YES"
            buildForArchiving="YES"
            buildForAnalyzing="YES">
            {ref(app_target, "PythonCoach.app", "app")}
         </BuildActionEntry>
         <BuildActionEntry
            buildForTesting="YES"
            buildForRunning="NO"
            buildForProfiling="NO"
            buildForArchiving="NO"
            buildForAnalyzing="NO">
            {ref(test_target, "PythonCoachTests.xctest", "tests")}
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration="Debug"
      selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv="YES">
      <Testables>
         <TestableReference
            skipped="NO"
            parallelizable="YES">
            {ref(test_target, "PythonCoachTests.xctest", "tests")}
         </TestableReference>
      </Testables>
   </TestAction>
   <LaunchAction
      buildConfiguration="Debug"
      selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB"
      launchStyle="0"
      useCustomWorkingDirectory="NO"
      ignoresPersistentStateOnLaunch="NO"
      debugDocumentVersioning="YES"
      debugServiceExtension="internal"
      allowLocationSimulation="YES">
      <BuildableProductRunnable
         runnableDebuggingMode="0">
         {ref(app_target, "PythonCoach.app", "app")}
      </BuildableProductRunnable>
   </LaunchAction>
   <ProfileAction
      buildConfiguration="Release"
      shouldUseLaunchSchemeArgsEnv="YES"
      savedToolIdentifier=""
      useCustomWorkingDirectory="NO"
      debugDocumentVersioning="YES">
      <BuildableProductRunnable
         runnableDebuggingMode="0">
         {ref(app_target, "PythonCoach.app", "app")}
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration="Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration="Release"
      revealArchiveInOrganizer="YES">
   </ArchiveAction>
</Scheme>
"""


if __name__ == "__main__":
    main()
