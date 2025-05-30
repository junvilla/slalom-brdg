BridgeCTL also supports automation scenarios where you don't want an interactive UI, you just want to build and run bridge containers from the command-line. You can build bridge images, run bridge container, and remove bridge containers.

## Examples
- Build bridge image with docker

  `bridgectl --build`  


- Start a bridge container in local docker using the most recenly built bridge image.

  `bridgectl --run --token t1` 


- Remove a bridge container in local docker

  `bridgectl --remove --token t2` 



Note that the `bridgectl/config/bridge_settings.yml`, `bridge_tokens.yml` and `app_settings.yml` should be populated before running bridgectl with command-line parameters.


When running the `bridgectl` with any parameters, the above commands will be executed directly. When started without parameters, the bridgectl interactive command-line wizard will provide a menu of options like "Start UI", etc.

### Copying Configuration Settings Across Machines
Users can configure settings on one machine using the BridgeCTL UI and then copy the configuration files to a target machine and use the command-line to build and run containers in a headless linux environment.


- `bridgectl/config/bridge_settings.yml`
Contains settings for building the bridge image, including drivers, RPM version, etc.
- `bridgectl/config/app_settings.yml`
Stores application settings, including the selected image tag used when running the container.
- `bridgectl/config/bridge_tokens.yml`
Holds authentication tokens, target site, and target pool information used when running the agent.

## Notes
The bridgectl --run command works only for running bridge containers in Docker, not Kubernetes. To run BridgeCTL in Kubernetes, users can write a bash scripts to start bridge pods. But you can use the same bridge container image created by BridgeCTL.

