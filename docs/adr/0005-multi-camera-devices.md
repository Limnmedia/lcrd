# 0005 — Multi-camera devices

## Context

Phones and imaging devices commonly contain multiple physical imagers with
different roles and geometry.

## Decision

Model `device → camera_module → sensor`. Module roles such as main, telephoto,
and ultrawide remain distinct. A device does not receive one universal sensor.

## Why

Collapsing modules would assign the wrong physical geometry whenever an image
comes from a non-main camera. Intel RealSense records likewise identify the
RGB module rather than pretending the depth and color imagers are one sensor.

## Consequences

Consumers may need module metadata or user confirmation. The generic RED DSMC2
platform is similarly retained without choosing a sensor variant by guess.
