package cft

import (
	"bytes"
	"errors"
	"fmt"
	"strings"
	"text/template"
)

var metricFilterTemplate = template.Must(template.New("metricFilter").Parse(`resource.type=gcs_bucket AND
logName=projects/{{.Project.ID}}/logs/cloudaudit.googleapis.com%2Fdata_access AND
protoPayload.resourceName=projects/_/buckets/{{.Bucket.Name}} AND
protoPayload.status.code!=7 AND
protoPayload.authenticationInfo.principalEmail!=({{.ExpectedUsers}})
`))

// GCSBucket wraps a CFT Cloud Storage Bucket.
type GCSBucket struct {
	GCSBucketProperties `json:"properties"`
	ExpectedUsers       []string `json:"expected_users,omitempty"`
}

// GCSBucketProperties  represents a partial CFT bucket implementation.
type GCSBucketProperties struct {
	GCSBucketName string     `json:"name"`
	Location      string     `json:"location"`
	Bindings      []Binding  `json:"bindings"`
	Versioning    versioning `json:"versioning"`
	Logging       struct {
		LogBucket string `json:"logBucket"`
	} `json:"logging"`
}

type versioning struct {
	// Use pointer to differentiate between zero value and intentionally being set to false.
	Enabled *bool `json:"enabled"`
}

// Init initializes the bucket with the given project.
func (b *GCSBucket) Init(project *Project) error {
	if b.GCSBucketName == "" {
		return errors.New("name must be set")
	}
	if b.Location == "" {
		return errors.New("location must be set")
	}
	if b.Versioning.Enabled != nil && !*b.Versioning.Enabled {
		return errors.New("versioning must not be disabled")
	}

	t := true
	b.Versioning.Enabled = &t

	appendGroupPrefix := func(ss ...string) []string {
		res := make([]string, 0, len(ss))
		for _, s := range ss {
			res = append(res, "group:"+s)
		}
		return res
	}

	// Note: duplicate bindings are de-duplicated by deployment manager.
	defaultBindings := []Binding{
		{"roles/storage.admin", appendGroupPrefix(project.OwnersGroup)},
		{"roles/storage.objectAdmin", appendGroupPrefix(project.DataReadWriteGroups...)},
		{"roles/storage.objectViewer", appendGroupPrefix(project.DataReadOnlyGroups...)},
	}

	b.Bindings = MergeBindings(append(defaultBindings, b.Bindings...)...)

	logBucket := project.AuditLogs.LogsGCSBucket.Name
	if logBucket == "" {
		logBucket = project.ID + "-logs"
	}
	b.Logging.LogBucket = logBucket
	return nil
}

// Name returns the name of the bucket.
func (b *GCSBucket) Name() string {
	return b.GCSBucketName
}

// TemplatePath returns the name of the template to use for the bucket.
func (b *GCSBucket) TemplatePath() string {
	return "deploy/cft/templates/gcs_bucket.py"
}

// DependentResources gets the dependent resources of this bucket.
// If the bucket has expected users, this list will contain a metric that will detect unexpected
// access to the bucket from users not in the expected users list.
func (b *GCSBucket) DependentResources(project *Project) ([]parsedResource, error) {
	if len(b.ExpectedUsers) == 0 {
		return nil, nil
	}

	var buf bytes.Buffer
	data := struct {
		Project       *Project
		Bucket        *GCSBucket
		ExpectedUsers string
	}{
		project,
		b,
		strings.Join(b.ExpectedUsers, " AND "),
	}
	if err := metricFilterTemplate.Execute(&buf, data); err != nil {
		return nil, fmt.Errorf("failed to execute filter template: %v", err)
	}

	m := &Metric{
		MetricProperties: MetricProperties{
			MetricName:  "unexpected-access-" + b.Name(),
			Description: "Count of unexpected data access to " + b.Name(),
			Filter:      buf.String(),
			Descriptor: descriptor{
				MetricKind: "DELTA",
				ValueType:  "INT64",
				Unit:       "1",
				Labels: []label{{
					Key:         "user",
					ValueType:   "STRING",
					Description: "Unexpected user",
				}},
			},
			LabelExtractors: map[string]string{
				"user": "EXTRACT(protoPayload.authenticationInfo.principalEmail)",
			},
		},
	}
	return []parsedResource{m}, nil
}
