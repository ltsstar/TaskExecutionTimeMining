import numpy as np

class ArtificialModel:
    def __init__(self, *args, **kwargs):
        pass

    def sample(self, x_categorical : list, x_continuous : list, n : int = 1):
        concept = x_categorical[0]
        resource = x_categorical[1]
        resource_count = x_categorical[2:]
        known_resources = ['1', 'Clark', 'Jane', 'Joe', 'Karsten']
        resource_count = dict([(resource_name, int(rc)) for resource_name, rc in zip(known_resources, resource_count)])
        seconds_in_day = x_continuous[0]

        res = []
        for i in range(n):
            res.append(self.sample_single(concept, resource, resource_count, seconds_in_day))
        return (n, res)

    def sample_single(self, concept, resource, resource_count, seconds_in_day):
        return self.sample_single_hour(concept, resource, resource_count, seconds_in_day) * 3600

    def sample_single_hour(self, concept, resource, resource_count, seconds_in_day):
        if resource == "1":
            #DefaultResource
            return self.sample_default(concept)
        elif resource == "Jane":
            #JaneResource
            duration = self.sample_default(concept) * self.sample_earlybird_factor(seconds_in_day)
            if resource_count["Joe"]:
                duration *= np.random.lognormal(np.log(3), 0.1/3)
            return duration
        elif resource == "Joe":
            #JoeResource
            duration = self.sample_default(concept) + self.sample_coffee_drinker_offset()
            if resource_count["Jane"]:
                duration *= np.random.lognormal(np.log(2), 0.1/2)
            return duration
        elif resource == "Clark":
            #EarlyBirdResource
            return self.sample_default(concept) * self.sample_earlybird_factor(seconds_in_day)
        elif resource == "Karsten":
            #CoffeeTrinkerResource
            return self.sample_default(concept) + self.sample_coffee_drinker_offset()

    def sample_default(self, concept):
        if concept == "DIAGNOSIS":
            return np.random.lognormal(np.log(1), 0.2/1)
        elif concept == "REPAIR":
            return np.random.lognormal(np.log(6), 3/6)
        elif concept == "QUALITY_CONTROL":
            return np.random.lognormal(np.log(3), 0.5/3)

    def sample_earlybird_factor(self, seconds_in_day):
        current_hour = seconds_in_day / 3600
        if current_hour % 24 < 13:
            return np.random.uniform(0.6, 0.8)
        else:
            return np.random.uniform(1.2, 1.4)

    def sample_coffee_drinker_offset(self):
        if np.random.choice([True, False], size=1, p=[0.2, 0.8])[0]:
            coffee_duration = np.random.lognormal(np.log(10/60), 5/60/(10/60))
            return coffee_duration
        else:
            return 0