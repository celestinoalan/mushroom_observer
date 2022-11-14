# Classification of Mushroom Species based on Images and other Data

All analyses/models developed here are based on the data uploaded to the [Mushroom Observer](https://mushroomobserver.org/).

## Exploratory Data Analysis
- [EDA of tabular data](https://github.com/celestinoalan/mushroom_observer/blob/main/notebooks/eda_csv-alan-01.ipynb).

## Replicating this Environment
I am assuming you use linux. If you use conda, run
```
conda create --name <env> --file environment.yml

```

If you use pip, run
```
pip install -r requirements.txt
```

## Ideas

### How to Obtain Labels for an Observation
1. Consider all ranks together. Alternative: Use only one rank.
2. Map all IDs to the smallest ID within a synonym group that is not deprecated.
3. Should there be no non-deprecated ID within a synonym group, map all IDs from the group to the smallest deprecated ID within the group.

### Optimal Vote Cache
- Use a sample of the peak around 2.5 as a holdout set, check balanced precision for different values of vote cache. Use tabular model for this experiment.

### Tabular Model Feature Engineering
- We can map `lat` and `long` to `north`, `south`, `east`, and `west` in a tabular model.