// main.jsonnet
// Entry point for compilation: jsonnet -S -m . ./jsonnet/main.jsonnet
// Also executable in Hamster app via long-press "运行 main.jsonnet"

// Note: Full JSON/YAML definitions are compiled automatically into light/ and dark/
{
  'config.yaml': std.manifestYamlDoc(import 'Config.libsonnet'),
}
