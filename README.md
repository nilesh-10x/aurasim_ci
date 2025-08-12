# AuraSIM CI Action

A GitHub Action for running robotic simulations using AuraSIM in CI/CD pipelines. This action allows you to automate the testing of robotic software by running simulations in Docker containers with USD (Universal Scene Description) files.

## Features

- Run robotic simulations in CI/CD pipelines
- Docker-based execution for consistent environments
- Configurable timeout for simulation runs
- Support for USD (Universal Scene Description) files
- Input validation and error handling
- Simulation status tracking and logging

## Usage

### Basic Example

```yaml
name: Robot Simulation Test
on: [push, pull_request]

jobs:
  simulation:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run AuraSIM Simulation
        uses: auraml/aurasim_ci@main
        with:
          usd_path: './scenes/warehouse_robot.usd'
          robot_docker_image: 'myorg/robot-stack:latest'
          robot_start_cmd: 'python /app/start_simulation.py'
          timeout: '600'
```

### Advanced Example with Multiple Simulations

```yaml
name: Comprehensive Robot Testing
on: [push, pull_request]

jobs:
  simulation-matrix:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        scenario:
          - {
              scene: 'warehouse',
              timeout: '300',
              image: 'myorg/warehouse-robot:v1.0',
            }
          - {
              scene: 'factory',
              timeout: '450',
              image: 'myorg/factory-robot:v1.0',
            }
          - {
              scene: 'outdoor',
              timeout: '600',
              image: 'myorg/outdoor-robot:v1.0',
            }

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run ${{ matrix.scenario.scene }} Simulation
        uses: auraml/aurasim_ci@v1
        with:
          usd_path: './scenes/${{ matrix.scenario.scene }}_environment.usd'
          robot_docker_image: ${{ matrix.scenario.image }}
          robot_start_cmd: 'ros2 launch robot_bringup simulation.launch'
          timeout: ${{ matrix.scenario.timeout }}
```

## Inputs

| Input                | Description                                                           | Required | Default |
| -------------------- | --------------------------------------------------------------------- | -------- | ------- |
| `usd_path`           | Path to the USD (Universal Scene Description) file for the simulation | Yes      | -       |
| `robot_docker_image` | Docker image containing the robot software stack                      | Yes      | -       |
| `robot_start_cmd`    | Command to start the robot in the container                           | Yes      | -       |
| `timeout`            | Timeout for the simulation in seconds                                 | No       | `300`   |

## Requirements

### Docker Image Requirements

Your robot Docker image should:

- Have all necessary robot software installed (ROS, navigation stack, etc.)
- Accept the simulation command via the entry point or CMD
- Handle graceful shutdown on timeout signals
- Output logs and results to expected locations

### USD File Requirements

- Must be a valid USD (Universal Scene Description) file
- Should contain the complete simulation environment
- Must be accessible in the repository or workspace

## Environment Variables

The action sets up these environment variables in the Docker container:

- `USD_PATH`: Path to the USD file within the container
- `OUTPUT_DIR`: Directory for simulation outputs
- `SIMULATION_START_TIME`: Timestamp when simulation started

## Error Handling

The action will fail if:

- The specified USD file doesn't exist
- The Docker image cannot be pulled or found
- The simulation times out
- The robot command exits with a non-zero status

## License

This project is licensed under the terms specified in the LICENSE file.
