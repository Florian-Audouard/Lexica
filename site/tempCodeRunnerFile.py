th tqdm(total=len(liste_line)) as pbar:
                for line in liste_line:
                    add_line(line, liste_langue)
                    pbar.update()