import argparse
import sys
import os
import time

from isaacsim import SimulationApp

# Configuration for headless simulation optimized for CI
CONFIG = {
    "width": 1280,
    "height": 720,
    "sync_loads": True,
    "headless": True,
    "renderer": "RaytracedLighting"
}


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser("AuraSIM CI USD Stage Loader")
    parser.add_argument(
        "--usd_path", type=str, help="Path to USD file", required=True
    )
    parser.add_argument(
        "--headless", default=True, action="store_true", help="Run stage headless"
    )
    parser.add_argument(
        "--timeout", type=int, default=300, help="Simulation timeout in seconds"
    )
    parser.add_argument(
        "--output_dir", type=str, default="/output", help="Output directory for logs"
    )

    args, unknown = parser.parse_known_args()

    # Ensure headless mode for CI
    CONFIG["headless"] = args.headless

    print(f"Starting Isaac Sim with USD: {args.usd_path}")
    print(f"Headless mode: {args.headless}")
    print(f"Timeout: {args.timeout} seconds")

    # Start the omniverse application
    kit = SimulationApp(launch_config=CONFIG)

    import carb
    import omni

    try:
        # Check if USD file exists
        if not os.path.exists(args.usd_path):
            carb.log_error(f"USD file not found: {args.usd_path}")
            kit.close()
            sys.exit(1)

        print(f"Loading USD stage: {args.usd_path}")

        # Open the USD stage
        omni.usd.get_context().open_stage(args.usd_path)

        # Wait two frames so that stage starts loading
        kit.update()
        kit.update()

        print("Loading stage...")
        from isaacsim.core.utils.stage import is_stage_loading

        # Wait for stage to load completely
        stage_load_start = time.time()
        while is_stage_loading():
            kit.update()
            if time.time() - stage_load_start > 60:  # 60 second timeout for loading
                carb.log_error("Stage loading timed out")
                kit.close()
                sys.exit(1)

        print("✅ Stage loading complete")

        # Start timeline/simulation
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        print("🎬 Simulation started")

        # Create stop signal file checker
        stop_signal_path = "/tmp/stop_simulation"
        simulation_start = time.time()

        print("🔄 Simulation running... (waiting for stop signal or timeout)")

        # Main simulation loop
        while kit.is_running():
            # Check for stop signal file
            if os.path.exists(stop_signal_path):
                print("🛑 Stop signal received, shutting down...")
                break

            # Check timeout
            if time.time() - simulation_start > args.timeout:
                print(f"⏰ Simulation timeout reached ({args.timeout}s)")
                break

            # Update simulation
            kit.update()
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

        # Stop timeline
        timeline.stop()
        print("⏹️  Simulation stopped")

        # Write completion status
        status_file = os.path.join(args.output_dir, "simulation_status.txt")
        with open(status_file, "w") as f:
            f.write("completed\n")

        print("✅ Simulation completed successfully")

    except Exception as e:
        carb.log_error(f"Simulation error: {str(e)}")

        # Write error status
        status_file = os.path.join(args.output_dir, "simulation_status.txt")
        with open(status_file, "w") as f:
            f.write(f"error: {str(e)}\n")

        kit.close()
        sys.exit(1)

    finally:
        kit.close()


if __name__ == "__main__":
    main()
