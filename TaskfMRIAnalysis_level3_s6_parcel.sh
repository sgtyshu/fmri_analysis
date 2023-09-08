#!/bin/bash

CARET7DIR='/usr/local/neurosoft/workbench/bin_linux64'
FSLDIR='/usr/local/neurosoft/fsl6.0.3/bin'

. /usr/local/neurosoft/fsl6.0.3/etc/fslconf/fsl.sh
# 指定要遍历的目录

base_dir="/nfs/t2/raven/data/bold/derivatives/ciftify"
pscalar_dir="/nfs/h1/userhome/liyifan/workingdir/Raven-fmri/result/level2_pcope/"
parcel_group_anova_result_dir="/nfs/t2/raven/data/bold/derivatives/ciftify/parcel_group_anova_result_flame1_dof_s6"
parcel_group_anova_result_fsf_dir="/nfs/t2/raven/data/bold/derivatives/ciftify/parcel_group_anova_result_flame1_dof_s6/fsf"
parcel_group_anova_result_flameo_dir="/nfs/t2/raven/data/bold/derivatives/ciftify/parcel_group_anova_result_flame1_dof_s6/flameo_result"
original_fsf_dir="/nfs/h1/userhome/liyifan/workingdir/Raven-fmri/fsf/group_anova/"
mask_dof_dir="/nfs/t2/raven/data/bold/derivatives/ciftify/res4d/threshold_res4d/"
CIFTItemplate_dir="/nfs/h1/userhome/liyifan/workingdir/Raven-fmri/result/level2_pcope/"


if [ -e ${parcel_group_anova_result_dir} ] ; then
rm -r ${parcel_group_anova_result_dir}
mkdir ${parcel_group_anova_result_dir}
else
mkdir -p ${parcel_group_anova_result_dir}
fi

if [ -e ${parcel_group_anova_result_fsf_dir} ] ; then
rm -r ${parcel_group_anova_result_fsf_dir}
mkdir ${parcel_group_anova_result_fsf_dir}
else
mkdir -p ${parcel_group_anova_result_fsf_dir}
fi

varcope_index=1
cope_index=1

echo "Copying fsf files..."

for dir in "${base_dir}"/sub-*; do

    if [ -d "$dir" ]; then
        # 获取文件夹名称
        folder_name=$(basename "$dir")
        # 构建源文件路径
        cope_files=(
                    "_ses-raven_task-action_level2_cope_const_edge_number_hp200_s6.pscalar.nii"
                    "_ses-raven_task-action_level2_cope_const_obj_number_hp200_s6.pscalar.nii"
                    "_ses-raven_task-action_level2_cope_const_symbolic_number_hp200_s6.pscalar.nii"
                    "_ses-raven_task-action_level2_cope_dist3_edge_number_hp200_s6.pscalar.nii"
                    "_ses-raven_task-action_level2_cope_dist3_obj_number_hp200_s6.pscalar.nii"
                    "_ses-raven_task-action_level2_cope_dist3_symbolic_number_hp200_s6.pscalar.nii"
                    "_ses-raven_task-action_level2_cope_prog_edge_number_hp200_s6.pscalar.nii"
                    "_ses-raven_task-action_level2_cope_prog_obj_number_hp200_s6.pscalar.nii"
                    "_ses-raven_task-action_level2_cope_prog_symbolic_number_hp200_s6.pscalar.nii"
                    )
        for cope_file in "${cope_files[@]}"; do
            # 检查源文件是否存在
            source_file="${dir}/MNINonLinear/Results/ses-raven_task-action/ses-raven_task-action_hp200_s6_level2.feat/${folder_name}${cope_file}"
            if [ -f "$source_file" ]; then
                # 构建目标文件路径
                target_file="${parcel_group_anova_result_dir}/cope${cope_index}.pscalar.nii"
                # 复制文件
                cp "$source_file" "$target_file"
                echo "copying cope file: $target_file"
                ((cope_index++))  # cope 索引自增
            else
                echo "cope file does not exist: $source_file"
            fi
        done

    fi
done

cp ${original_fsf_dir}/level2_group.fsf ${parcel_group_anova_result_fsf_dir}/level2_group.fsf
cp ${original_fsf_dir}/level2_group.mat ${parcel_group_anova_result_fsf_dir}/level2_group.mat
cp ${original_fsf_dir}/level2_group.grp ${parcel_group_anova_result_fsf_dir}/level2_group.grp
cp ${original_fsf_dir}/level2_group.con ${parcel_group_anova_result_fsf_dir}/level2_group.con
cp ${original_fsf_dir}/level2_group.fts ${parcel_group_anova_result_fsf_dir}/level2_group.fts
cp ${mask_dof_dir}/mask_parcel.nii.gz ${parcel_group_anova_result_fsf_dir}/mask.nii.gz
cp ${mask_dof_dir}/dof.nii.gz ${parcel_group_anova_result_fsf_dir}/dof.nii.gz


Extension="pscalar.nii"
for CIFTI in ${parcel_group_anova_result_dir}/*.${Extension} ; do
    fakeNIFTI=$( echo $CIFTI | sed -e "s|.${Extension}|.nii.gz|" );
    ${CARET7DIR}/wb_command -cifti-convert -to-nifti $CIFTI $fakeNIFTI
    rm $CIFTI
    echo "converting $CIFTI to $fakeNIFTI"
done

###这里手动计算一下需要输入的文件数量
#每个被试现有9个within subject的cope文件，一共需要输入9*30个文件
fileCounter=270
####
mergeCounter=0;
COPEMERGE=""
VARCOPEMERGE=""
echo "Merging..."
while [ "$mergeCounter" -lt "${fileCounter}" ] ; do
    mergeCounter=$(($mergeCounter+1))
    COPEMERGE="${COPEMERGE}${parcel_group_anova_result_dir}/cope${mergeCounter}.nii.gz "
    VARCOPEMERGE="${VARCOPEMERGE}${parcel_group_anova_result_dir}/varcope${mergeCounter}.nii.gz "
    done
${FSLDIR}/fslmerge -t ${parcel_group_anova_result_dir}/copeMerged${mergeCounter}.nii.gz $COPEMERGE
${FSLDIR}/fslmerge -t ${parcel_group_anova_result_dir}/varcopeMerged${mergeCounter}.nii.gz $VARCOPEMERGE

#删除中间文件
mergeCounter=0;
echo "Deleting middle files..."
while [ "$mergeCounter" -lt "${fileCounter}" ] ; do
    mergeCounter=$(($mergeCounter+1))
    rm ${parcel_group_anova_result_dir}/cope${mergeCounter}.nii.gz
    rm ${parcel_group_anova_result_dir}/varcope${mergeCounter}.nii.gz
    done

echo "Running flameo for summary cope and varcope"
${FSLDIR}/flameo --cope=${parcel_group_anova_result_dir}/copeMerged${fileCounter}.nii.gz \
                    --mask=${parcel_group_anova_result_fsf_dir}/mask.nii.gz \
                    --ld=${parcel_group_anova_result_flameo_dir} \
                    --dm=${parcel_group_anova_result_fsf_dir}/level2_group.mat \
                    --cs=${parcel_group_anova_result_fsf_dir}/level2_group.grp \
                    --tc=${parcel_group_anova_result_fsf_dir}/level2_group.con \
                    --fc=${parcel_group_anova_result_fsf_dir}/level2_group.fts \
                    --runmode=flame1

echo "Converting back to ptseries.nii..."
CIFTItemplate="${CIFTItemplate_dir}/sub-30_ses-raven_task-action_level2_cope_prog_symbolic_number_hp200_s6.pscalar.nii"
for fakeNIFTI in ${parcel_group_anova_result_flameo_dir}/*.nii.gz; do
    CIFTI=$( echo $fakeNIFTI | sed -e "s|.nii.gz|.ptseries.nii|" );
    #这行代码的作用是将${fakeNIFTI}变量中的文件名扩展名.nii.gz替换为.ptseries.nii，并将替换后的文件名赋值给CIFTI变量
    if [[ $fakeNIFTI == *"zfstat1"* ]]; then	
        ${FSLDIR}/fslmaths $fakeNIFTI -ztop $fakeNIFTI'_pval'
        ${CARET7DIR}/wb_command -cifti-convert -from-nifti ${fakeNIFTI%/*}/zfstat1_pval.nii.gz $CIFTItemplate ${fakeNIFTI%/*}/zfstat1_rules_pval.ptseries.nii -reset-timepoints 1 1
        ${CARET7DIR}/wb_command -cifti-convert-to-scalar ${fakeNIFTI%/*}/zfstat1_rules_pval.ptseries.nii ROW ${fakeNIFTI%/*}/zfstat1_rules_pval.pscalar.nii
        ${CARET7DIR}/wb_command -cifti-convert -from-nifti $fakeNIFTI $CIFTItemplate $CIFTI -reset-timepoints 1 1
        ${CARET7DIR}/wb_command -cifti-convert-to-scalar ${fakeNIFTI%/*}/zfstat1.ptseries.nii ROW ${fakeNIFTI%/*}/zfstat1_rules.pscalar.nii
        rm ${fakeNIFTI%/*}/zfstat1.ptseries.nii
        rm ${fakeNIFTI%/*}/zfstat1_pval.nii.gz
        rm ${fakeNIFTI%/*}/zfstat1_rules_pval.ptseries.nii
    fi
    if [[ $fakeNIFTI == *"zfstat2"* ]]; then	
        ${FSLDIR}/fslmaths $fakeNIFTI -ztop $fakeNIFTI'_pval'
        ${CARET7DIR}/wb_command -cifti-convert -from-nifti ${fakeNIFTI%/*}/zfstat2_pval.nii.gz $CIFTItemplate ${fakeNIFTI%/*}/zfstat2_attribute_pval.ptseries.nii -reset-timepoints 1 1
        ${CARET7DIR}/wb_command -cifti-convert-to-scalar ${fakeNIFTI%/*}/zfstat2_attribute_pval.ptseries.nii ROW ${fakeNIFTI%/*}/zfstat2_attribute_pval.pscalar.nii
        ${CARET7DIR}/wb_command -cifti-convert -from-nifti $fakeNIFTI $CIFTItemplate $CIFTI -reset-timepoints 1 1
        ${CARET7DIR}/wb_command -cifti-convert-to-scalar ${fakeNIFTI%/*}/zfstat2.ptseries.nii ROW ${fakeNIFTI%/*}/zfstat2_attribute.pscalar.nii
        rm ${fakeNIFTI%/*}/zfstat2.ptseries.nii
        rm ${fakeNIFTI%/*}/zfstat2_pval.nii.gz
        rm ${fakeNIFTI%/*}/zfstat2_attribute_pval.ptseries.nii

    fi
    if [[ $fakeNIFTI == *"zfstat3"* ]]; then	
        ${FSLDIR}/fslmaths $fakeNIFTI -ztop $fakeNIFTI'_pval'
        ${CARET7DIR}/wb_command -cifti-convert -from-nifti ${fakeNIFTI%/*}/zfstat3_pval.nii.gz $CIFTItemplate ${fakeNIFTI%/*}/zfstat3_interaction_pval.ptseries.nii -reset-timepoints 1 1
        ${CARET7DIR}/wb_command -cifti-convert-to-scalar ${fakeNIFTI%/*}/zfstat3_interaction_pval.ptseries.nii ROW ${fakeNIFTI%/*}/zfstat3_interaction_pval.pscalar.nii
        ${CARET7DIR}/wb_command -cifti-convert -from-nifti $fakeNIFTI $CIFTItemplate $CIFTI -reset-timepoints 1 1
        ${CARET7DIR}/wb_command -cifti-convert-to-scalar ${fakeNIFTI%/*}/zfstat3.ptseries.nii ROW ${fakeNIFTI%/*}/zfstat3_interaction.pscalar.nii
        rm ${fakeNIFTI%/*}/zfstat3_pval.nii.gz
        rm ${fakeNIFTI%/*}/zfstat3_interaction_pval.ptseries.nii
        rm ${fakeNIFTI%/*}/zfstat3.ptseries.nii
    fi
    ${CARET7DIR}/wb_command -cifti-convert -from-nifti $fakeNIFTI $CIFTItemplate $CIFTI -reset-timepoints 1 1
    rm $fakeNIFTI
done
echo "Finished!"