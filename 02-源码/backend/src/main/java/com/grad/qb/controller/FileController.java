package com.grad.qb.controller;

import com.grad.qb.common.BizEx;
import com.grad.qb.common.R;
import com.grad.qb.common.UserContext;
import com.grad.qb.entity.SysFile;
import com.grad.qb.mapper.SysFileMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** 文件上传：校验扩展名与大小，按 uploads/{bizType}/{yyyyMM}/uuid.ext 落盘，数据库只存相对路径 */
@RestController
@RequestMapping("/api/file")
public class FileController {

    private static final List<String> IMG = List.of("jpg", "jpeg", "png", "webp");
    private static final List<String> DOC = List.of("pdf", "docx", "xlsx", "csv");
    private final SysFileMapper fileMapper;

    @Value("${app.upload-dir:./uploads}")
    private String uploadDir;

    public FileController(SysFileMapper fileMapper) {
        this.fileMapper = fileMapper;
    }

    @PostMapping("/upload")
    public R<Map<String, Object>> upload(@RequestParam("file") MultipartFile file,
                                         @RequestParam(defaultValue = "common") String bizType) throws IOException {
        if (file == null || file.isEmpty()) throw new BizEx(4000, "请选择要上传的文件");
        String original = file.getOriginalFilename() == null ? "file" : file.getOriginalFilename();
        String ext = original.contains(".") ? original.substring(original.lastIndexOf('.') + 1).toLowerCase() : "";
        if (!IMG.contains(ext) && !DOC.contains(ext)) throw new BizEx(4000, "仅支持 jpg/png/webp/pdf/docx/xlsx/csv");
        boolean isImg = IMG.contains(ext);
        long limit = (isImg ? 5L : 20L) * 1024 * 1024;
        if (file.getSize() > limit) throw new BizEx(4000, isImg ? "图片不能超过 5MB" : "文档不能超过 20MB");
        String month = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMM"));
        String name = UUID.randomUUID().toString().replace("-", "") + "." + ext;
        Path dir = Paths.get(uploadDir, bizType, month).toAbsolutePath().normalize();
        Files.createDirectories(dir);
        file.transferTo(dir.resolve(name).toFile());
        String rel = "/uploads/" + bizType + "/" + month + "/" + name;
        SysFile sf = new SysFile();
        sf.setFileName(original);
        sf.setFilePath(rel);
        sf.setFileSize(file.getSize());
        sf.setFileType(ext);
        sf.setBizType(bizType);
        sf.setUploaderId(UserContext.id());
        fileMapper.insert(sf);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("fileName", original);
        data.put("filePath", rel);
        data.put("path", rel);
        data.put("fileSize", file.getSize());
        data.put("fileType", ext);
        return R.ok(data);
    }
}
