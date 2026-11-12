# hydrodemo

`hydrodemo` is a teaching package for rainfall-runoff modeling. It provides:

- Synthetic rainfall forcing
- Synthetic "observed" streamflow generated from known parameters
- A gamma distributed unit hydrograph model
- Calibration with Generalized Likelihood Uncertainty Estimation (GLUE)
- Standard evaluation metrics such as NSE and KGE

## Installation

```bash
pip install hydrodemo
```

For development, install [pixi](https://pixi.sh), clone the repository, and run:

```bash
pixi install
pixi run check
```
