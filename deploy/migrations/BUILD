# Independent tools that converts yaml files.

package(default_visibility = ["//visibility:public"])

licenses(["notice"])  # Apache 2.0

load("@deploy_deps//:requirements.bzl", "requirement")

py_binary(
    name = "project_splitter",
    srcs = ["project_splitter.py"],
    deps = [
        requirement("absl-py"),
        "//deploy/utils",
    ],
)

py_test(
    name = "project_splitter_test",
    srcs = ["project_splitter_test.py"],
    data = [
        "//deploy/samples:configs",
    ],
    python_version = "PY3",
    deps = [
        requirement("absl-py"),
        ":project_splitter",
        "//deploy/utils",
    ],
)
