# Classification of Mushroom Species based on Images and other Data

All analyses/models developed here are based on the data uploaded to the [Mushroom Observer](https://mushroomobserver.org/).

## Exploratory Data Analysis
- [EDA of tabular data](https://github.com/celestinoalan/mushroom_observer/blob/main/notebooks/eda_csv-alan-01.ipynb).

## Ideas
### Optimal Vote Cache
- Use a sample of the peak around 2.5 as a holdout set, check balanced precision for different values of vote cache. Use tabular model for this experiment.

### Tabular Model Feature Engineering
- We can map `lat` and `long` to `north`, `south`, `east`, and `west` in a tabular model.