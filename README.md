# Credrails Reconciler

A tool that reads in two datasets, reconciles their records, and
produce a report detailing the differences between the two.

## Usage

Please ensure you have Python 12+ installed before proceeding.

1. Clone the project and run the following command to install the application, and
its dependencies:

    ```bash
    pip install -e .[dev,test,docs]
    ```

2. Run the following command on your terminal to use the tool.

    ```bash
    credrails-reconciler /path/to/source.csv /path/to/target.csv
    ```

   Replace `/path/to/source.csv` and `/path/to/target.csv` with a path to a valid source.csv and target.csv respectively.

3. To get prettier output, run:

    ```bash
   credrails-reconciler /path/to/source.csv /path/to/target.csv -w pretty-writer
    ```

4. To persist the output on a CSV file, run:

   ```bash
   credrails-reconciler /path/to/source.csv /path/to/target.csv -w csv-writer -o output.csv
   ```

5. To see the available options, run:

   ```bash
   credrails-reconciler --help
   ```

## License

[MIT License](https://github.com/kennedykori/credrails-reconciler/blob/develop/LICENSE)

Copyright (c) 2024, Kennedy Kori
