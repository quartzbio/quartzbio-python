QuartzBio Import Shortcut Example
======================

Make sure you're using the newest version of QuartzBio with `pip install quartzbio --upgrade`

The QuartzBio Python client provides a simple command line shortcut to import data.

To run the example commands, download the [example_input.json](https://github.com/quartzbio/quartzbio-python/blob/master/examples/import/example_input.json) and [example_template.json](https://github.com/quartzbio/quartzbio-python/blob/master/examples/import/example_template.json) files.

In your command line:
```bash
quartzbio import --create-dataset test-dataset example_input.json
```

This dataset will be placed at the root of your personal vault.  You can specify values for the `--vault` and `--path` flags
to place the dataset into a different vault, or into a particular folder within the target vault.

If you wish to add QuartzBio entities to your data, you can do so by using a template file (you can also do it later on the QuartzBio web interface).
```bash
quartzbio import --create-dataset test-dataset example_input.json --template-file example_template.json
```

To get a full list of the arguments options available, try
```bash
quartzbio import -h
```
