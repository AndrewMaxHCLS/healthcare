package(default_visibility = ["//visibility:public"])

licenses(["notice"])  # Apache 2.0

load("@io_bazel_rules_go//go:def.bzl", "go_library", "go_test")

go_library(
    name = "go_default_library",
    srcs = [
        "bigquery_dataset.go",
        "binding.go",
        "cft.go",
        "default_resource.go",
        "deployment.go",
        "gcs_bucket.go",
        "gke_cluster.go",
        "gke_workload.go",
        "metric.go",
        "pubsub.go",
        "resourcepair.go",
    ],
    data = [
        "//deploy/cft/templates",
        "//deploy/templates",
    ],
    importpath = "github.com/GoogleCloudPlatform/healthcare/deploy/cft",
    deps = [
        "@com_github_imdario_mergo//:go_default_library",
        "@in_ghodss_yaml//:go_default_library",
    ],
)

go_test(
    name = "go_default_test",
    srcs = [
        "bigquery_dataset_test.go",
        "cft_test.go",
        "default_resource_test.go",
        "deployment_test.go",
        "gcs_bucket_test.go",
        "gke_cluster_test.go",
        "gke_workload_test.go",
        "metric_test.go",
        "pubsub_test.go",
        "resourcepair_test.go",
    ],
    embed = [":go_default_library"],
    deps = [
        "@com_github_google_cmp//cmp:go_default_library",
        "@in_ghodss_yaml//:go_default_library",
    ],
)
