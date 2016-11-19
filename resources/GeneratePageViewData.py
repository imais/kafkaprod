#!/usr/bin/env python
"""
Based off of https://github.com/apache/spark/blob/master/examples/src/main/scala/org/apache/spark/examples/streaming/clickstream/PageViewGenerator.scala
"""

import random
import argparse
import os

DEFAULT_TSV_FILE_NAME = "pageView.tsv"

# 100 randomly generated websites
PAGES = {
    "www.eurythermal.com": 0.0154984,
    "www.sequestrum.com": 0.01546521,
    "www.perfunctory.com": 0.015366135,
    "www.monstership.com": 0.0148106,
    "www.nonprofession.com": 0.014767281,
    "www.archididascalian.com": 0.014432758,
    "www.constitutor.com": 0.013840596,
    "www.biodynamics.com": 0.013838938,
    "www.euphonym.com": 0.013728722,
    "www.guitarist.com": 0.013689004,
    "www.tantivy.com": 0.013548628,
    "www.Florissant.com": 0.013454382,
    "www.parodist.com": 0.013354641,
    "www.sarcologist.com": 0.013321946,
    "www.Spatangoidea.com": 0.013222586,
    "www.potentness.com": 0.013148196,
    "www.seraphism.com": 0.013136356,
    "www.spookdom.com": 0.013122637,
    "www.chronist.com": 0.013052935,
    "www.tautness.com": 0.012829784,
    "www.unevoked.com": 0.012772467,
    "www.overstudiousness.com": 0.012751278,
    "www.circular.com": 0.012521653,
    "www.ultratense.com": 0.012345959,
    "www.Pithecolobium.com": 0.01231485,
    "www.Gothish.com": 0.011923083,
    "www.slangy.com": 0.011849055,
    "www.bladderwort.com": 0.011817495,
    "www.epauliere.com": 0.011669504,
    "www.umangite.com": 0.011666377,
    "www.scotale.com": 0.011517553,
    "www.catabaptist.com": 0.011515682,
    "www.asparaginic.com": 0.011419969,
    "www.louse.com": 0.011372552,
    "www.prospectiveness.com": 0.011271231,
    "www.Semecarpus.com": 0.011214939,
    "www.idiotize.com": 0.011176523,
    "www.qualminess.com": 0.011017529,
    "www.pictorially.com": 0.010932152,
    "www.uninhabitedness.com": 0.01090902,
    "www.scrat.com": 0.010906796,
    "www.dermorhynchous.com": 0.010851137,
    "www.precostal.com": 0.010840997,
    "www.undeterring.com": 0.010826928,
    "www.Hester.com": 0.010781237,
    "www.epauliere.com": 0.010616612,
    "www.papery.com": 0.010509744,
    "www.lienteria.com": 0.010349942,
    "www.seelful.com": 0.010272702,
    "www.underogating.com": 0.010252678,
    "www.overwoven.com": 0.01022624,
    "www.mendacity.com": 0.010182466,
    "www.unreprimanded.com": 0.010129475,
    "www.unrevolting.com": 0.009920584,
    "www.figured.com": 0.009665301,
    "www.unharmed.com": 0.009662194,
    "www.manny.com": 0.009652835,
    "www.taver.com": 0.009503452,
    "www.kenno.com": 0.009209905,
    "www.daytime.com": 0.009090392,
    "www.unbashfulness.com": 0.009004536,
    "www.neuromimesis.com": 0.008985376,
    "www.outhue.com": 0.00896848,
    "www.wingable.com": 0.008961752,
    "www.roughcast.com": 0.008855742,
    "www.Consolamentum.com": 0.008821476,
    "www.ununiformly.com": 0.008453745,
    "www.karyological.com": 0.008315002,
    "www.benzoperoxide.com": 0.00829248,
    "www.oinomancy.com": 0.008242576,
    "www.transudatory.com": 0.00815427,
    "www.biopsic.com": 0.008098073,
    "www.analgize.com": 0.008090922,
    "www.tum.com": 0.008068966,
    "www.thermochemically.com": 0.008029109,
    "www.proboscidiform.com": 0.008007984,
    "www.diathermacy.com": 0.007940213,
    "www.uninhabitedness.com": 0.007932422,
    "www.cyanoguanidine.com": 0.007824072,
    "www.Saponaria.com": 0.007786057,
    "www.Gothish.com": 0.00772298,
    "www.orthopedical.com": 0.007573406,
    "www.pinulus.com": 0.007482187,
    "www.antideflation.com": 0.007449738,
    "www.unimmortal.com": 0.007322589,
    "www.prezygapophysial.com": 0.007226995,
    "www.feasibleness.com": 0.006911013,
    "www.swangy.com": 0.006238266,
    "www.Llandovery.com": 0.006127649,
    "www.quad.com": 0.005822778,
    "www.choralcelo.com": 0.005818644,
    "www.transcorporeal.com": 0.005746321,
    "www.unobservantness.com": 0.005566397,
    "www.bozal.com": 0.005500202,
    "www.theologicopolitical.com": 0.005488297,
    "www.transudatory.com": 0.00540937,
    "www.merciful.com": 0.004862372,
    "www.monstership.com": 0.004614512,
    "www.phytonic.com": 0.002723574,
    "www.verbid.com": 0.002499231
}


HTTP_STATUS = {
    200: 0.95,
    404: 0.05
}

USER_ZIP_CODE = {
    12180: 0.5,
    61801: 0.3,
    93106: 0.1,
    96822: 0.1
}

USER_ID = dict((key, 0.01) for key in range(1, 101))


class PageView:
    """
    Class to hold page view info
    """
    def __init__(self, url, status, zip_code, user_id):
        self.url = url
        self.status = status
        self.zip_code = zip_code
        self.user_id = user_id

    def __str__(self):
        return "%s\t%s\t%s\t%s\n" % (self.url, self.status, self.zip_code, self.user_id)


def pick_from_distribution(input_map):
    """
    Generates an item from a distribution map
    :param input_map: The dictionary of items to their probabilities
    :return: An item from the dictionary
    """
    rand = random.random()
    total = 0.0
    for item, prob in input_map.iteritems():
        total += prob
        if total > rand:
            return item

    # shouldn't get here if probabilities
    return random.choice(input_map.keys())


def get_next_click_event():
    """
    Generates a PageView click event
    :return: A PageView object holding the click event
    """
    url = pick_from_distribution(PAGES)
    user_id = pick_from_distribution(USER_ID)
    status = pick_from_distribution(HTTP_STATUS)
    zip_code = pick_from_distribution(USER_ZIP_CODE)
    return PageView(url, status, zip_code, user_id)


def parse_args():
    """
    Parses the args passed to the program
    :return: An args object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_views", "-n", type=int, required=True)
    parser.add_argument("--output", "-o", default=DEFAULT_TSV_FILE_NAME)
    args = parser.parse_args()
    assert args.num_views >= 0, "Number of views must be greater than or equal to 0"
    return args


def main():
    args = parse_args()

    # ensure path exists if absolute
    if os.path.isabs(args.output):
        dirname = os.path.dirname(args.output)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    with open(args.output, 'w') as out:
        for i in range(0, args.num_views):
            page_view = get_next_click_event()
            out.write(str(page_view))


if __name__ == '__main__':
    main()

