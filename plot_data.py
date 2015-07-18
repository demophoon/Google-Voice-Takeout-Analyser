#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import func

from model import (
    Contact,
    Message,
    create_session,
)


def main():
    session = create_session()
    date_format = '%Y-%m-%W'
    results = session.query(
        func.strftime(date_format, Message.sent),
        func.sum(Message.polarity),
        func.count(Message.id),
    ).join(Contact).filter(
        Contact.name == "Me",
    ).group_by(
        func.strftime(date_format, Message.sent),
    ).all()

    # width = .35
    x_axis_labels = [x[1][0] for x in enumerate(results) if x[0] % 10 == 0]
    x_axis = [x[0] for x in enumerate(results)]
    y_axis = [x[1]/x[2] for x in results]

    print "Samples: {}".format(len(x_axis))

    plt.bar(x_axis, y_axis)
    plt.xticks(
        np.arange(min(x_axis), max(x_axis), 10),
        x_axis_labels,
        rotation=45,
        horizontalalignment='center',
    )

    plt.savefig('output.png', pad_inches=0.1)


if __name__ == '__main__':
    main()
