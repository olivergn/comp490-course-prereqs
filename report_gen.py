import neo4j_course_metrics as ncom

def print_degree_report(driver, papers):
    ind_sum = 0
    cp_ind_sum = 0
    outd_sum = 0
    cp_outd_sum = 0
    td_sum = 0
    cp_td_sum = 0

    max_ind = 0
    max_cp_ind = 0
    max_outd = 0
    max_cp_outd = 0
    max_td = 0
    max_cp_td = 0

    for paper in papers:
        ind = ncom.get_indegree(driver, paper)
        cp_ind = ncom.get_course_path_indegree(driver, paper)
        outd = ncom.get_outdegree(driver, paper)
        cp_outd = ncom.get_course_path_outdegree(driver, paper)
        td = ncom.get_total_degree(driver, paper)
        cp_td = ncom.get_total_course_path_degree(driver, paper)

        ind_sum += ind
        cp_ind_sum += cp_ind
        outd_sum += outd
        cp_outd_sum += cp_outd
        td_sum += td
        cp_td_sum += cp_td

        max_ind = ind if ind > max_ind else max_ind
        max_cp_ind = cp_ind if cp_ind > max_cp_ind else max_cp_ind
        max_outd = outd if outd > max_outd else max_outd
        max_cp_outd = cp_outd if cp_outd > max_cp_outd else max_cp_outd
        max_td = td if td > max_td else max_td
        max_cp_td = cp_td if cp_td > max_cp_td else max_cp_td

        print(f"{paper} & {ind:.2f} & {cp_ind:.2f} & {outd:.2f} & {cp_outd:.2f} & {td:.2f} & {cp_td:.2f} \\\\ \\hline")

    print("\n\nSummary:\n")

    print(f"Mean in-degree: {(ind_sum / len(papers)):.2f}")
    print(f"Mean course path in-degree: {(cp_ind_sum / len(papers)):.2f}")
    print(f"Mean out-degree: {(outd_sum / len(papers)):.2f}")
    print(f"Mean course path out-degree: {(cp_outd_sum / len(papers)):.2f}")
    print(f"Mean total degree: {(td_sum / len(papers)):.2f}")
    print(f"Mean total course path degree: {(cp_td_sum / len(papers)):.2f}")

    print(f"Max in-degree: {max_ind:.2f}")
    print(f"Max course path in-degree: {max_cp_ind:.2f}")
    print(f"Max out-degree: {max_outd:.2f}")
    print(f"Max course path out-degree: {max_cp_outd:.2f}")
    print(f"Max total degree: {max_td:.2f}")
    print(f"Max total course path degree: {max_cp_td:.2f}")

def print_weighted_report(driver, papers):
    w_ind_sum = 0
    w_cp_ind_sum = 0
    w_outd_sum = 0
    w_cp_outd_sum = 0
    w_td_sum = 0
    w_cp_td_sum = 0

    max_w_ind = 0
    max_w_cp_ind = 0
    max_w_outd = 0
    max_w_cp_outd = 0
    max_w_td = 0
    max_w_cp_td = 0

    for paper in papers:
        w_ind = ncom.get_weighted_indegree(driver, paper)
        w_cp_ind = ncom.get_weighted_course_path_indegree(driver, paper)
        w_outd = ncom.get_weighted_outdegree(driver, paper)
        w_cp_outd = ncom.get_weighted_course_path_outdegree(driver, paper)
        w_td = ncom.get_total_weighted_degree(driver, paper)
        w_cp_td = ncom.get_total_weighted_course_path_degree(driver, paper)

        w_ind_sum += w_ind
        w_cp_ind_sum += w_cp_ind
        w_outd_sum += w_outd
        w_cp_outd_sum += w_cp_outd
        w_td_sum += w_td
        w_cp_td_sum += w_cp_td

        max_w_ind = w_ind if w_ind > max_w_ind else max_w_ind
        max_w_cp_ind = w_cp_ind if w_cp_ind > max_w_cp_ind else max_w_cp_ind
        max_w_outd = w_outd if w_outd > max_w_outd else max_w_outd
        max_w_cp_outd = w_cp_outd if w_cp_outd > max_w_cp_outd else max_w_cp_outd
        max_w_td = w_td if w_td > max_w_td else max_w_td
        max_w_cp_td = w_cp_td if w_cp_td > max_w_cp_td else max_w_cp_td

        print(f"{paper} & {w_ind:.2f} & {w_cp_ind:.2f} & {w_outd:.2f} & {w_cp_outd:.2f} & {w_td:.2f} & {w_cp_td:.2f} \\\\ \\hline")

    print("\n\nSummary:\n")

    print(f"Mean weighted in-degree: {(w_ind_sum / len(papers)):.2f}")
    print(f"Mean weighted course path in-degree: {(w_cp_ind_sum / len(papers)):.2f}")
    print(f"Mean weighted out-degree: {(w_outd_sum / len(papers)):.2f}")
    print(f"Mean weighted course path out-degree: {(w_cp_outd_sum / len(papers)):.2f}")
    print(f"Mean weighted total degree: {(w_td_sum / len(papers)):.2f}")
    print(f"Mean weighted total course path degree: {(w_cp_td_sum / len(papers)):.2f}")

    print(f"Max weighted in-degree: {max_w_ind:.2f}")
    print(f"Max weighted course path in-degree: {max_w_cp_ind:.2f}")
    print(f"Max weighted out-degree: {max_w_outd:.2f}")
    print(f"Max weighted course path out-degree: {max_w_cp_outd:.2f}")
    print(f"Max total weighted degree: {max_w_td:.2f}")
    print(f"Max total weighted course path degree: {max_w_cp_td:.2f}")

def print_misc_report(driver, papers):
    ocs_sum = 0
    wdi_sum = 0
    be_sum = 0
    nc_be_sum = 0
    pr_sum = 0
    nc_pr_sum = 0

    max_ocs = 0
    max_wdi = 0
    max_be = 0
    max_nc_be = 0
    max_pr = 0
    max_nc_pr = 0

    for paper in papers:
        ocs = ncom.get_outcomponent_size(driver, paper)
        wdi = ncom.get_weighted_downstream_impact(driver, paper)
        be = ncom.get_betweenness(driver, paper)
        nc_be = ncom.get_no_connectors_betweenness(driver, paper)
        pr = ncom.get_pagerank(driver, paper)
        nc_pr = ncom.get_no_connectors_pagerank(driver, paper)

        ocs_sum += ocs
        wdi_sum += wdi
        be_sum += be
        nc_be_sum += nc_be
        pr_sum += pr
        nc_pr_sum += nc_pr

        max_ocs = ocs if ocs > max_ocs else max_ocs
        max_wdi = wdi if wdi > max_wdi else max_wdi
        max_be = be if be > max_be else max_be
        max_nc_be = nc_be if nc_be > max_nc_be else max_nc_be
        max_pr = pr if pr > max_pr else max_pr
        max_nc_pr = nc_pr if nc_pr > max_nc_pr else max_nc_pr

        print(f"{paper} & {ocs:.2f} & {wdi:.2f} & {be:.2f} & {nc_be:.2f} & {pr:.2f} & {nc_pr:.2f} \\\\ \\hline")

    print("\n\nSummary:\n")

    print(f"Mean out-component size: {(ocs_sum / len(papers)):.2f}")
    print(f"Mean weighted downstream impact: {(wdi_sum / len(papers)):.2f}")
    print(f"Mean betweenness: {(be / len(papers)):.2f}")
    print(f"Mean no connectors betweenness: {(nc_be / len(papers)):.2f}")
    print(f"Mean PageRank: {(pr / len(papers)):.2f}")
    print(f"Mean no connectors PageRank: {(nc_pr / len(papers)):.2f}")

    print(f"Max out-component size: {max_ocs:.2f}")
    print(f"Max weighted downstream impact: {max_wdi:.2f}")
    print(f"Max betweenness: {max_be:.2f}")
    print(f"Max no connectors betweenness: {max_nc_be:.2f}")
    print(f"Max PageRank: {max_pr:.2f}")
    print(f"Max no connectors PageRank: {max_nc_pr:.2f}")
