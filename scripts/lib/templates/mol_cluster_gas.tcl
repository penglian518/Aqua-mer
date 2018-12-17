#! /usr/bin/tclsh

set psf "mol.psf"
# Replace the catdcd PATH with the one on your system. 
# e.g. "/home/p6n/tools/vmd-1.9.2/lib/vmd/plugins/LINUXAMD64/bin/catdcd5.1/catdcd"
set catdcd "/home/p6n/tools/vmd-1.9.2/lib/vmd/plugins/LINUXAMD64/bin/catdcd5.1/catdcd"

set outfile [open mol_cluster_gas.dat w]
set outfil2 [open mol_rmsdtt_gas.dat w]

set w1 7
set w2 30
set title [format "%-*s" $w1 "frame"]

# cluster analysis on lowest 3 temperature replicas
for {set j 0} {$j <= 2} {incr j} {
    set dcd "output_gas/$j/mol.job0.$j.dcd"
    mol load psf $psf dcd $dcd
    set nf [molinfo top get numframes]
    set frame0 [atomselect top "all" frame 1]
    set sel [atomselect top "all"]
    append title [format "%-*s" $w2 "mol$j"]
    
    #measures RMSD for each frame aligning to frame 0
    for {set i 1} {$i <= $nf} {incr i} {
        $sel frame $i
        $sel move [measure fit $sel $frame0]
        set outline([list $j $i]) [format "%-*s" $w2 "[measure rmsd $sel $frame0]"]
    }
    
    #finds clusters for each replica, writing a temp dcd for each frame and then combining them to one dcd per cluster
    set clust [measure cluster $sel num NCLUSTERS distfunc rmsd cutoff CUTOFF]
    puts $outfile $clust

    set h 0
    foreach cluster $clust {
            set k 0
            foreach frame $cluster {
                animate write dcd temp$k.dcd beg $frame end $frame sel $sel waitfor all top
                incr k
                }
            set lf [llength $cluster]
            puts $lf
            if {$lf > 1} {
                for {set l 0} {$l < [expr $lf-1]} {incr l} {
                    set m [expr $l+1]
                    exec $catdcd -o temp.dcd temp$l.dcd temp$m.dcd
                    exec mv temp.dcd temp$m.dcd
                    exec rm temp$l.dcd
                }
                exec mv temp$m.dcd clusters_gbis/cluster$j.$h.dcd
            }
        incr h
    }
}

puts $outfil2 $title
for {set h 1} {$h <=$nf} {incr h} {
    set newline [format "%-*s" $w1 $h]
    puts $outfil2 "$newline $outline([list 0 $h]) $outline([list 1 $h]) $outline([list 2 $h])"
}

close $outfile
close $outfil2
exit
EOF
