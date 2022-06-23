
import doc2vec_FK as d2v
import run_gan_classifier as gan

from matplotlib import pyplot as plt

import time
import shutil
import numpy as np
import json
import os, sys


def test_n_times(n, gen_dim=10, method="classical", calc_embeddings=True, save_results=True, par_number=-1):
    """Run the gan_classifier n times and save the results in json files
    Saves the results after prediction in a json file and the train_hist after training (including all losses) in a json file as well.

    Args:
        n (int): amount of runs of the gan_classifer
        gen_dim (int, optional): Set the depth of the generator models Encoder and Decoder. Not currently implemented. Defaults to 10.
        method (str, optional): classical or quantum. Only needed for setting the file path for saving the results. Defaults to "classical".
        calc_embeddings (bool, optional): Set to caclulate new embeddings each time you run the classifier. Defaults to True.
        save_results (bool, optional): Save the prediction results and the training histories in seperate json files. Defaults to True.
        par_number (int, optional): Save the results to a specific "part" file of the complete result. Defaults to -1.

    Returns:
        list, list: all prediction results, all training histories
    """

    results = {
        "classical": [],
        "quantum": []
    }
    train_hists = {
        "classical": [],
        "quantum": []
    }
    for _ in range(n):
        # first check if new embeddings have to be calculated
        if calc_embeddings:
            # move all existing input files
            for f in os.listdir("input_data"):
                if os.path.isfile(f):
                    shutil.move("input_data/" + f, "input_text/" + f)

            d2v.main(True, False, False, 150, "dm", "input_data/")
        
        for meth in train_hists.keys():
            train_hist = gan.main("train", meth)
            if train_hist == None:
                print("Train history was None. Check log.log file")
            else:
                train_hists[meth].append(train_hist)

            res = gan.main("predict", meth)
            if res != None:
                results[meth].append(res)


    new_results = {
        "classical": [],
        "quantum": []
    }
    for meth, ress in results.items(): # FK: to avoid some json and int64 errors
        for res in ress:
            tmp = dict()
            for k, v in res.items():
                if isinstance(v, list):
                    tmp[k] = int(v[0])
                else:
                    tmp[k] = float(v)
            new_results[meth].append(tmp)
    if save_results:
        with open(str(method) + "_results_" + str(n) + "times" + (str("_" + str(par_number)) if int(par_number)!=-1 else "") + ".json", 'w',
                  encoding="utf-8") as res_fd: 
            json.dump(new_results, res_fd)

    new_hists = {
        "classical": [],
        "quantum": []
    }
    for meth, hists in train_hists.items():
        for hist in hists:
            tmp = dict()
            for k, vs in hist.items():
                if isinstance(vs, list):
                    tmp[k] = []
                    for v in vs:
                        if isinstance(v, float):
                            tmp[k].append(float(v))
                        elif isinstance(v, int):
                            tmp[k].append(float(v))
                        else:
                            tmp[k].append(str(v))
                else:
                    tmp[k] = vs
            new_hists[meth].append(tmp)
    if save_results:
        with open(str(method) + "_train_hists_" + str(n) + "times" + (str("_" + str(par_number)) if int(par_number)!=-1 else "") + ".json", 'w',
                  encoding="utf-8") as hist_fd:
            json.dump(new_hists, hist_fd)

    return new_results, new_hists


def merge_par_results(n=35, method="classical", file_path='./'):
    """Merge the part results of parallel run test runs.
    Save them all together in one json file

    Args:
        n (int, optional): amount of runs of the gan_classifer. Defaults to 35.
        method (str, optional): classical or quantum. Only needed for setting the file path for saving the results. Defaults to "classical".
        file_path (str, optional): the location in which the separated runs are located. Defaults to './'.

    Returns:
        int: the amount of test runs
    """
    for res_type in ["results", "train_hists"]:
        amount = 0
        print(res_type)
        all_classical = []
        all_quantum = []
        for file in os.listdir(file_path):
            if method in file and res_type in file: # and file.endswith(".json")
                with open(file_path + file, 'r', encoding="utf-8") as js_fd:
                    one_result = json.load(js_fd)
                    [all_classical.append(cla) for cla in one_result["classical"]]
                    [all_quantum.append(cla) for cla in one_result["quantum"]]
                amount += 1
        complete_results = {
            "classical": all_classical,
            "quantum": all_quantum
        }
        with open(str(method) + '_' + str(res_type) + '_' + str(int(amount)) + "times.json", 'w', encoding="utf-8") as js_fd:
            json.dump(complete_results, js_fd)
    
    return amount




def display_results(n=35, method="classical", save_plots=True):
    """Load the saved results from a test run and display them in plots.
    Display MCC and threshold after prediction and the losses after training.

    Args:
        n (int, optional): amount of runs of the gan_classifier. Needed for reading the correct file path. Defaults to 35.
        method (str, optional): classical or quantum. Needed for reading the correct file path. Defaults to "classical".
        save_plots (bool, optional): Create and save plot of MCC, threshold and losses if True. Defaults to True.
    """
    with open(str(method) + "_results_" + str(n) + "times.json", 'r', encoding="utf-8") as res_fd:
        results = json.load(res_fd)

    print("MCC class: " + str(np.mean([x["MCC"] for x in results["classical"]])) + " (mean), " + str(np.median([x["MCC"] for x in results["classical"]])) + " (median), " + str(np.std([x["MCC"] for x in results["classical"]])) + " (st dev)")
    print("threshold class: " + str(np.mean([x["threshold"] for x in results["classical"]])) + " (mean), " + str(np.median([x["threshold"] for x in results["classical"]])) + " (median), " + str(np.std([x["threshold"] for x in results["classical"]])) + " (st dev)")

    print("MCC quan: " + str(np.mean([x["MCC"] for x in results["quantum"]])) + " (mean), " + str(np.median([x["MCC"] for x in results["quantum"]])) + " (median), " + str(np.std([x["MCC"] for x in results["quantum"]])) + " (st dev)")
    print("threshold quan: " + str(np.mean([x["threshold"] for x in results["quantum"]])) + " (mean), " + str(np.median([x["threshold"] for x in results["quantum"]])) + " (median), " + str(np.std([x["threshold"] for x in results["quantum"]])) + " (st dev)")

    if save_plots:
        ##### MCC
        for meth, color in zip(["classical", "quantum"], ["blue", "black"]):
            plt.scatter([i for i in range(n)], [x["MCC"] for x in results[meth]],
                        c=[color for _ in range(n)], label=meth)
        plt.ylim(0, 1)
        plt.title("MCC after prediction")
        plt.ylabel("MCC")
        plt.xlabel("runs")
        plt.legend()
        plt.savefig(str(method) + "_MCC_" + str(n) + "times.png", bbox_inches="tight")
        plt.cla()
        plt.clf()

        plt.boxplot([[x["MCC"] for x in results["classical"]], [x["MCC"] for x in results["quantum"]]], showmeans=True, labels=["classical", "quantum"])
        plt.ylabel("MCC")
        plt.savefig(str(method) + "_MCC_boxplot_" + str(n) + "times.png", bbox_inches="tight")
        plt.cla()
        plt.clf()

        ##### MCC with threshold
        for meth, color in zip(["classical", "quantum"], ["blue", "black"]):
            plt.plot([i for i in range(n)], [x["MCC"] for x in results[meth]], color=color, label=f"MCC-{meth}")
            plt.plot([i for i in range(n)], [x["threshold"] for x in results[meth]], color=color,
                     linestyle="dashed", label=f"optimized anomaly threshold-{meth}")
        plt.ylim(0, 1)
        plt.title("MCC and optimized anomaly threshold after prediciton")
        plt.legend()
        plt.xlabel("runs")
        plt.savefig(str(method) + "_MCC_threshold_" + str(n) + "times.png", bbox_inches="tight")
        plt.cla()
        plt.clf()

        ##### Threshold
        for meth, color in zip(["classical", "quantum"], ["blue", "black"]):
            plt.scatter([i for i in range(n)], [x["threshold"] for x in results[meth]],
                        c=[color for _ in range(n)], label=meth)
        plt.title("Threshold after prediction")
        plt.xlabel("runs")
        plt.ylabel("threshold")
        plt.legend()
        plt.savefig(str(method) + "_threshold_" + str(n) + "times.png", bbox_inches="tight")
        plt.cla()
        plt.clf()

    with open(str(method) + "_train_hists_" + str(n) + "times.json", 'r', encoding="utf-8") as hist_fd:
        train_hists = json.load(hist_fd)
    if save_plots and not save_plots: # TODO remove
        ##### all losses separately
        for loss in ["contextual_loss", "adversarial_loss", "encoder_loss", "generator_loss", "discriminator_loss"]:
            for i in range(len(train_hists)):
                plt.plot(train_hists[i]["step_number"], [i for i in train_hists[i][loss]]) # if i < 1000 else 0
            plt.title(loss)
            plt.xlabel("runs")
            plt.savefig(str(method) + '_' + str(loss) + '_' + str(n) + "times.png", bbox_inches="tight")
            plt.cla()
            plt.clf()
        
        ##### all losses in one
        for loss, color in zip(["contextual_loss", "adversarial_loss", "encoder_loss", "generator_loss", "discriminator_loss"], ["green", "red", "blue", "black", "purple"]):
            for i in range(len(train_hists)):
                line, = plt.plot(train_hists[i]["step_number"], [i for i in train_hists[i][loss]], color=color) # if i < 1000 else 0 
            line.set_label(loss) # FK: only add the label once
        plt.title("All five losses over all runs")
        plt.legend()
        plt.xlabel("runs")
        plt.savefig(str(method) + "_all_losses_" + str(n) + "times.png", bbox_inches="tight")
        plt.cla()
        plt.clf()


def test_latent_dimensions(latent_dim_range, latent_dim_steps, each_run_n, method):
    """_summary_

    Args:
        latent_dim_range (tupel): (start of range, end of range)
        latent_dim_steps (int): amount of steps
        each_run_n (_type_): _description_
        method (_type_): _description_
    """
    all_MCC_means = []
    for dim in [int(x) for x in np.linspace(latent_dim_range[0], latent_dim_range[1], latent_dim_steps)]:
        print(dim)
        test_n_times(n=each_run_n, method=method, latent_dims=dim)
        pred_results, train_hists = display_results(n=each_run_n, method=method, save_plots=False)
        all_MCC_means.append(np.mean([x["MCC"] for x in pred_results]))
    
    plt.plot(np.linspace(latent_dim_range[0], latent_dim_range[1], latent_dim_steps), all_MCC_means)
    plt.title("mean MCCs for different latent dimensions")
    plt.ylabel("mean MCC")
    plt.xlabel("latent dimensions")
    plt.savefig(f"{method}_meanMC_latDim{latent_dim_range[0]}_{latent_dim_range[1]}_{latent_dim_steps}steps.png", bbox_inches="tight")
    plt.cla()
    plt.clf()

    return all_MCC_means


if __name__ == "__main__":
    tic = time.perf_counter()

    parallel_number = -1
    if len(sys.argv) > 1:
        parallel_number = sys.argv[1]
    n = 1
    method = "both"

    # test_n_times(n=n, method=method, calc_embeddings=False, par_number=parallel_number)
    n = merge_par_results(n=n, method=method, file_path="saved_results/single_input_mult_circ/200Steps_sep/")
    display_results(n=n, method=method, save_plots=True)

    toc = time.perf_counter()
    print("Total runtime: ", toc-tic)