#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import func, or_, and_

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
        func.strftime('%m-%d-%Y', Message.sent),
    ).join(Contact).filter(
        and_(
            Contact.name == "Me",
            Message.polarity != 0,
            Message.subjectivity >= .9,
        )
    ).group_by(
        func.strftime(date_format, Message.sent),
    ).order_by(
        Message.sent.asc()
    ).all()

    # width = .35
    axis_every = 10 * 1

    x_axis_labels = [
        x[1][3] for x in enumerate(results) if x[0] % axis_every == 0]
    x_axis = [x[0] for x in enumerate(results)]
    y_axis = [x[1]/x[2] for x in results]
    colors = map(lambda v: {True: 'g', False: 'r'}[v > 0], y_axis)
    #y_axis = map(abs, y_axis)

    print "Samples: {}".format(len(x_axis))

    plt.rcParams["figure.figsize"][0] = 21.0
    plt.rcParams["figure.figsize"][1] = 9.0
    plt.rcParams["figure.autolayout"] = True

    plt.bar(x_axis, y_axis, linewidth=0, color=colors)
    plt.grid(b=True, which='major', linestyle='-')
    plt.title('Positive or Negative calculated sentiment of sent text messages per week')
    plt.ylabel("Calculated percentage of sentiment per message")
    plt.xlabel("Date")
    plt.xticks(
        np.arange(min(x_axis), max(x_axis), axis_every),
        x_axis_labels,
        rotation=35,
        horizontalalignment='center',
    )
    plt.xlim([min(x_axis) - 0.5, max(x_axis) + 0.5])
    plt.ylim([min(y_axis) - .1, max(y_axis) + .1])

    print plt.rcParams["figure.figsize"]

    plt.savefig('output.png')


if __name__ == '__main__':
    main()
