from anytree import Node, RenderTree
import sys
import pydicom


def recurse_tree(parent, dataset, hide=False):
    # order the dicom tags
    for data_element in dataset:
        nhex = hex(id(data_element))
        node_id = str(data_element)
        #tree.hlist.add(node_id, text=str(data_element))
        node = Node(node_id, parent)
        #if hide:
            #tree.hlist.hide_entry(node_id)

        if data_element.VR == "SQ":  # a sequence
            for i, dataset in enumerate(data_element.value):
                item_id = node_id + "." + str(i + 1)
                sq_item_description = data_element.name.replace(
                    " Sequence", "")  # XXX not i18n
                item_text = "{0:s} {1:d}".format(sq_item_description, i + 1)
                n = Node(item_text, node)

                if "ConceptNameCodeSequence" in dataset:
                    cncs = dataset.ConceptNameCodeSequence[0].CodeValue
                    if cncs == "121070":
                        # Findings
                        if "ContentSequence" in dataset:
                            cs = dataset.ContentSequence
                            for innerds in cs:
                                if "ConceptNameCodeSequence" in innerds:
                                    innercncs = innerds.ConceptNameCodeSequence[0].CodeValue
                                    if innercncs == "T-46820":
                                        print('<<<<< Uterine Artery >>>>>>')
                                        if "ContentSequence" in innerds:
                                            for _ds in innerds.ContentSequence:
                                                if "ConceptNameCodeSequence" in _ds:
                                                    _cv = _ds.ConceptNameCodeSequence[0].CodeValue
                                                    if _cv == "G-C171":
                                                        # Laterality
                                                        if "ConceptCodeSequence" in _ds:
                                                            if _ds.ConceptCodeSequence[0].CodeValue == "G-A100":
                                                                laterality = "droit"
                                                            else:
                                                                laterality = "gauche"
                                                            #print("Laterality", laterality)
                                                    else:
                                                        #print(_cv)
                                                        if "ConceptNameCodeSequence" in _ds:
                                                            _ccs = _ds.ConceptNameCodeSequence[0]
                                                            if "MeasuredValueSequence" in _ds:
                                                                for valitem in _ds.MeasuredValueSequence:
                                                                    val = valitem.NumericValue
                                                                    #print(f"{_ccs.CodeValue} ({_ccs.CodeMeaning}) = {val}")
                                if innercncs == "T-F1810":
                                    print('<<<<< Umbilical Artery >>>>>>')
                                    if "ContentSequence" in innerds:
                                        for _ds in innerds.ContentSequence:
                                            if "ConceptNameCodeSequence" in _ds:
                                                _cv = _ds.ConceptNameCodeSequence[0].CodeValue
                                                if _cv == "11951-1":
                                                    foetusId = _ds.TextValue
                                                    print("Foetus ID", foetusId)
                                                else:
                                                    # print(_cv)
                                                    if "ConceptNameCodeSequence" in _ds:
                                                        _ccs = _ds.ConceptNameCodeSequence[0]
                                                        if "MeasuredValueSequence" in _ds:
                                                            for valitem in _ds.MeasuredValueSequence:
                                                                val = valitem.NumericValue
                                                                print(f"{_ccs.CodeValue} ({_ccs.CodeMeaning}) = {val}")


                    #print('ConceptNameCodeSequence', cncs)
                #n = Node(item_id + " -> " + item_text, node)
                #tree.hlist.hide_entry(item_id)
                recurse_tree(n, dataset, hide=True)


if __name__ == '__main__':

    ds = pydicom.dcmread('./data/drsidhom/sr_75454533.dcm')

    root = Node("ROOT") #root

    recurse_tree(root, ds, False)

    #for pre, fill, node in RenderTree(root):
    #    print("%s%s" % (pre, node.name))


    """if len(sys.argv) != 2:
        print("Please supply a dicom file name:\n")
        print(usage)
        sys.exit(-1)

    file = sys.argv[1]
    root = tkinter_tix.Tk()
    root.geometry("{0:d}x{1:d}+{2:d}+{3:d}".format(1200, 900, 0, 0))
    root.title("DICOM tree viewer - " + file)

    RunTree(root, file)
    root.mainloop()
    """